"""
Advanced AWS Textract AnalyzeDocument processor with enhanced features
"""
import boto3
import json
from typing import Dict, Any, List, Optional, Tuple
from botocore.exceptions import ClientError
import cv2
import numpy as np
from PIL import Image
import io

class AnalyzeDocumentProcessor:
    def __init__(self, region_name: str = 'us-east-1'):
        self.textract_client = boto3.client('textract', region_name=region_name)
        self.comprehend_client = boto3.client('comprehend', region_name=region_name)
        
        # Enhanced feature configurations
        self.w2_field_patterns = {
            'employee_ssn': r'\d{3}-\d{2}-\d{4}',
            'employer_ein': r'\d{2}-\d{7}',
            'wages': r'\$?[\d,]+\.?\d*',
            'tax_withheld': r'\$?[\d,]+\.?\d*'
        }
        
        self.bank_statement_patterns = {
            'account_number': r'\d{8,12}',
            'routing_number': r'\d{9}',
            'transaction_amount': r'[\+\-]?\$?[\d,]+\.?\d*',
            'date': r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}'
        }
    
    def analyze_document_enhanced(self, document_bytes: bytes, doc_type: str) -> Dict[str, Any]:
        """Enhanced document analysis with advanced features"""
        try:
            # Pre-process image for better OCR
            processed_image = self._preprocess_image(document_bytes)
            
            # Analyze document with all features
            response = self.textract_client.analyze_document(
                Document={'Bytes': processed_image},
                FeatureTypes=['FORMS', 'TABLES', 'LAYOUT', 'SIGNATURES']
            )
            
            # Enhanced parsing with ML validation
            result = self._enhanced_parsing(response, doc_type)
            
            # Add confidence analysis
            result['confidence_analysis'] = self._advanced_confidence_analysis(response)
            
            # Add document quality metrics
            result['quality_metrics'] = self._calculate_quality_metrics(document_bytes)
            
            return result
            
        except ClientError as e:
            raise Exception(f"AnalyzeDocument processing error: {str(e)}")
    
    def _preprocess_image(self, image_bytes: bytes) -> bytes:
        """Preprocess image for better OCR accuracy"""
        try:
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Apply image enhancement techniques
            # 1. Noise reduction
            denoised = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)
            
            # 2. Contrast enhancement
            lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # 3. Sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            # Convert back to bytes
            _, buffer = cv2.imencode('.png', sharpened)
            return buffer.tobytes()
            
        except Exception as e:
            # If preprocessing fails, return original
            return image_bytes
    
    def _enhanced_parsing(self, response: Dict, doc_type: str) -> Dict[str, Any]:
        """Enhanced parsing with document-specific logic"""
        blocks = response.get('Blocks', [])
        
        if doc_type == 'w2':
            return self._parse_w2_enhanced(blocks)
        elif doc_type == 'bank_statement':
            return self._parse_bank_statement_enhanced(blocks)
        
        return self._parse_generic_document(blocks)
    
    def _parse_w2_enhanced(self, blocks: List[Dict]) -> Dict[str, Any]:
        """Enhanced W-2 parsing with field validation"""
        w2_data = {
            'employee_info': {
                'ssn': None,
                'name': None,
                'address': None
            },
            'employer_info': {
                'ein': None,
                'name': None,
                'address': None
            },
            'tax_info': {
                'wages': None,
                'federal_tax_withheld': None,
                'social_security_wages': None,
                'social_security_tax_withheld': None,
                'medicare_wages': None,
                'medicare_tax_withheld': None
            },
            'boxes': {},  # All W-2 boxes
            'validation_results': {}
        }
        
        # Extract all key-value pairs
        key_value_pairs = self._extract_enhanced_key_value_pairs(blocks)
        
        # W-2 specific field mappings with multiple possible keys
        field_mappings = {
            'employee_ssn': ['social security number', 'ssn', 'employee ssn'],
            'employee_name': ['employee name', 'name'],
            'employer_ein': ['employer identification', 'ein', 'employer ein'],
            'employer_name': ['employer name', 'company name'],
            'wages': ['wages', 'wages tips', 'box 1'],
            'federal_tax_withheld': ['federal income tax', 'federal tax', 'box 2'],
            'social_security_wages': ['social security wages', 'box 3'],
            'medicare_wages': ['medicare wages', 'box 5']
        }
        
        # Enhanced field extraction with fuzzy matching
        for field, possible_keys in field_mappings.items():
            value = self._find_best_match(key_value_pairs, possible_keys)
            if value:
                # Validate field format
                validated_value = self._validate_field_format(field, value)
                if 'employee' in field:
                    category = field.replace('employee_', '')
                    w2_data['employee_info'][category] = validated_value
                elif 'employer' in field:
                    category = field.replace('employer_', '')
                    w2_data['employer_info'][category] = validated_value
                else:
                    w2_data['tax_info'][field] = validated_value
        
        # Extract W-2 boxes (1-20)
        w2_data['boxes'] = self._extract_w2_boxes(blocks)
        
        # Validate extracted data
        w2_data['validation_results'] = self._validate_w2_data(w2_data)
        
        return {
            'document_type': 'w2',
            'extracted_data': w2_data,
            'processing_metadata': {
                'total_blocks': len(blocks),
                'extraction_method': 'enhanced_analyze_document'
            }
        }
    
    def _parse_bank_statement_enhanced(self, blocks: List[Dict]) -> Dict[str, Any]:
        """Enhanced bank statement parsing with transaction analysis"""
        statement_data = {
            'account_info': {
                'account_number': None,
                'routing_number': None,
                'account_holder': None,
                'bank_name': None
            },
            'statement_period': {
                'start_date': None,
                'end_date': None
            },
            'balances': {
                'beginning_balance': None,
                'ending_balance': None,
                'average_balance': None
            },
            'transactions': [],
            'summary': {
                'total_deposits': 0,
                'total_withdrawals': 0,
                'transaction_count': 0
            }
        }
        
        # Extract tables (transaction data)
        tables = self._extract_enhanced_tables(blocks)
        
        # Parse transactions with enhanced logic
        for table in tables:
            transactions = self._parse_transaction_table_enhanced(table)
            statement_data['transactions'].extend(transactions)
        
        # Calculate summary statistics
        statement_data['summary'] = self._calculate_transaction_summary(
            statement_data['transactions']
        )
        
        # Extract account information
        key_value_pairs = self._extract_enhanced_key_value_pairs(blocks)
        account_mappings = {
            'account_number': ['account number', 'account #', 'acct'],
            'routing_number': ['routing', 'routing number', 'aba'],
            'account_holder': ['account holder', 'customer name', 'name']
        }
        
        for field, possible_keys in account_mappings.items():
            value = self._find_best_match(key_value_pairs, possible_keys)
            if value:
                statement_data['account_info'][field] = value
        
        return {
            'document_type': 'bank_statement',
            'extracted_data': statement_data,
            'processing_metadata': {
                'total_blocks': len(blocks),
                'extraction_method': 'enhanced_analyze_document'
            }
        }
    
    def _advanced_confidence_analysis(self, response: Dict) -> Dict[str, Any]:
        """Advanced confidence analysis with statistical metrics"""
        blocks = response.get('Blocks', [])
        confidences = []
        
        confidence_by_type = {
            'WORD': [],
            'LINE': [],
            'KEY_VALUE_SET': [],
            'TABLE': []
        }
        
        for block in blocks:
            if 'Confidence' in block:
                conf = block['Confidence']
                confidences.append(conf)
                
                block_type = block['BlockType']
                if block_type in confidence_by_type:
                    confidence_by_type[block_type].append(conf)
        
        if not confidences:
            return {'error': 'No confidence scores available'}
        
        # Calculate comprehensive statistics
        analysis = {
            'overall': {
                'mean': np.mean(confidences),
                'median': np.median(confidences),
                'std_dev': np.std(confidences),
                'min': np.min(confidences),
                'max': np.max(confidences),
                'percentile_25': np.percentile(confidences, 25),
                'percentile_75': np.percentile(confidences, 75)
            },
            'by_block_type': {}
        }
        
        for block_type, confs in confidence_by_type.items():
            if confs:
                analysis['by_block_type'][block_type] = {
                    'mean': np.mean(confs),
                    'count': len(confs),
                    'min': np.min(confs),
                    'max': np.max(confs)
                }
        
        # Quality assessment
        mean_confidence = analysis['overall']['mean']
        if mean_confidence >= 95:
            quality = 'excellent'
        elif mean_confidence >= 85:
            quality = 'good'
        elif mean_confidence >= 70:
            quality = 'fair'
        else:
            quality = 'poor'
        
        analysis['quality_assessment'] = quality
        
        return analysis
    
    def _calculate_quality_metrics(self, image_bytes: bytes) -> Dict[str, Any]:
        """Calculate document quality metrics"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Calculate various quality metrics
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Brightness
            brightness = np.mean(gray)
            
            # Contrast (standard deviation)
            contrast = np.std(gray)
            
            # Resolution
            height, width = gray.shape
            resolution = width * height
            
            return {
                'sharpness': float(sharpness),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'resolution': resolution,
                'dimensions': {'width': width, 'height': height}
            }
            
        except Exception as e:
            return {'error': f'Could not calculate quality metrics: {str(e)}'}
    
    def _find_best_match(self, key_value_pairs: Dict[str, str], 
                        possible_keys: List[str]) -> Optional[str]:
        """Find best matching key-value pair using fuzzy matching"""
        for key, value in key_value_pairs.items():
            key_lower = key.lower()
            for possible_key in possible_keys:
                if possible_key.lower() in key_lower:
                    return value
        return None
    
    def _validate_field_format(self, field_name: str, value: str) -> str:
        """Validate and format field values"""
        if field_name in self.w2_field_patterns:
            pattern = self.w2_field_patterns[field_name]
            # Add regex validation logic here
            pass
        
        return value  # Return cleaned/validated value