"""
Direct AWS Textract processor for document analysis
"""
import boto3
import json
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

class TextractProcessor:
    def __init__(self, region_name: str = 'us-east-1'):
        self.textract_client = boto3.client('textract', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
    
    def process_document_sync(self, document_bytes: bytes, doc_type: str) -> Dict[str, Any]:
        """Process document synchronously using Textract"""
        try:
            response = self.textract_client.detect_document_text(
                Document={'Bytes': document_bytes}
            )
            
            # Also get forms and tables
            forms_response = self.textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            return self._parse_textract_response(response, forms_response, doc_type)
            
        except ClientError as e:
            raise Exception(f"Textract processing error: {str(e)}")
    
    def process_document_async(self, s3_bucket: str, s3_key: str, doc_type: str) -> str:
        """Start asynchronous document processing"""
        try:
            response = self.textract_client.start_document_analysis(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': s3_bucket,
                        'Name': s3_key
                    }
                },
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            return response['JobId']
            
        except ClientError as e:
            raise Exception(f"Textract async processing error: {str(e)}")
    
    def get_async_results(self, job_id: str, doc_type: str) -> Dict[str, Any]:
        """Get results from asynchronous processing"""
        try:
            response = self.textract_client.get_document_analysis(JobId=job_id)
            
            if response['JobStatus'] == 'SUCCEEDED':
                return self._parse_textract_response(None, response, doc_type)
            elif response['JobStatus'] == 'FAILED':
                raise Exception(f"Textract job failed: {response.get('StatusMessage', 'Unknown error')}")
            else:
                return {'status': response['JobStatus'], 'job_id': job_id}
                
        except ClientError as e:
            raise Exception(f"Error getting async results: {str(e)}")
    
    def _parse_textract_response(self, text_response: Optional[Dict], 
                                forms_response: Dict, doc_type: str) -> Dict[str, Any]:
        """Parse Textract response based on document type"""
        
        if doc_type == 'w2':
            return self._parse_w2_document(text_response, forms_response)
        elif doc_type == 'bank_statement':
            return self._parse_bank_statement(text_response, forms_response)
        
        return {'raw_response': forms_response}
    
    def _parse_w2_document(self, text_response: Optional[Dict], 
                          forms_response: Dict) -> Dict[str, Any]:
        """Parse W-2 specific fields from Textract response"""
        w2_fields = {
            'employee_ssn': None,
            'employee_name': None,
            'employer_ein': None,
            'employer_name': None,
            'wages': None,
            'federal_tax_withheld': None,
            'social_security_wages': None,
            'medicare_wages': None
        }
        
        blocks = forms_response.get('Blocks', [])
        key_value_pairs = self._extract_key_value_pairs(blocks)
        
        # Map Textract fields to W-2 fields
        field_mappings = {
            'Employee\'s social security number': 'employee_ssn',
            'Employee\'s name': 'employee_name',
            'Employer identification number': 'employer_ein',
            'Employer\'s name': 'employer_name',
            'Wages, tips, other compensation': 'wages',
            'Federal income tax withheld': 'federal_tax_withheld'
        }
        
        for key, value in key_value_pairs.items():
            for mapping_key, field_name in field_mappings.items():
                if mapping_key.lower() in key.lower():
                    w2_fields[field_name] = value
                    break
        
        return {
            'document_type': 'w2',
            'extracted_fields': w2_fields,
            'confidence_scores': self._calculate_confidence_scores(blocks),
            'raw_key_value_pairs': key_value_pairs
        }
    
    def _parse_bank_statement(self, text_response: Optional[Dict], 
                             forms_response: Dict) -> Dict[str, Any]:
        """Parse bank statement specific fields from Textract response"""
        statement_data = {
            'account_number': None,
            'account_holder': None,
            'statement_period': None,
            'beginning_balance': None,
            'ending_balance': None,
            'transactions': []
        }
        
        blocks = forms_response.get('Blocks', [])
        
        # Extract tables (transactions)
        tables = self._extract_tables(blocks)
        statement_data['transactions'] = self._parse_transaction_tables(tables)
        
        # Extract key information
        key_value_pairs = self._extract_key_value_pairs(blocks)
        
        return {
            'document_type': 'bank_statement',
            'extracted_fields': statement_data,
            'confidence_scores': self._calculate_confidence_scores(blocks),
            'raw_key_value_pairs': key_value_pairs
        }
    
    def _extract_key_value_pairs(self, blocks: List[Dict]) -> Dict[str, str]:
        """Extract key-value pairs from Textract blocks"""
        key_value_pairs = {}
        
        for block in blocks:
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block.get('EntityTypes', []):
                    # This is a key block
                    key_text = self._get_text_from_relationships(block, blocks)
                    value_text = self._get_value_from_key_block(block, blocks)
                    if key_text and value_text:
                        key_value_pairs[key_text] = value_text
        
        return key_value_pairs
    
    def _extract_tables(self, blocks: List[Dict]) -> List[Dict]:
        """Extract table data from Textract blocks"""
        tables = []
        
        for block in blocks:
            if block['BlockType'] == 'TABLE':
                table_data = self._parse_table_block(block, blocks)
                tables.append(table_data)
        
        return tables
    
    def _get_text_from_relationships(self, block: Dict, all_blocks: List[Dict]) -> str:
        """Get text content from block relationships"""
        text_parts = []
        
        if 'Relationships' in block:
            for relationship in block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        child_block = next((b for b in all_blocks if b['Id'] == child_id), None)
                        if child_block and child_block['BlockType'] == 'WORD':
                            text_parts.append(child_block['Text'])
        
        return ' '.join(text_parts)
    
    def _calculate_confidence_scores(self, blocks: List[Dict]) -> Dict[str, float]:
        """Calculate confidence scores for extracted data"""
        confidences = []
        
        for block in blocks:
            if 'Confidence' in block:
                confidences.append(block['Confidence'])
        
        if confidences:
            return {
                'average': sum(confidences) / len(confidences),
                'minimum': min(confidences),
                'maximum': max(confidences)
            }
        
        return {'average': 0.0, 'minimum': 0.0, 'maximum': 0.0}