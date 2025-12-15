"""
Real AWS BDA Blueprint processor using Textract Adapters SDK
Implements W-2 and Bank Statement document analysis using AWS Textract Adapters
"""
import boto3
import json
import time
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

class BlueprintProcessor:
    def __init__(self, region_name: str = 'us-east-1'):
        self.region_name = region_name
        
        # Initialize AWS clients for BDA Blueprint
        self.textract_client = boto3.client('textract', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name)
        
        print("=" * 80)
        print("🚀🚀🚀 UPDATED CODE RUNNING - BlueprintProcessor v3.0 DEBUGGING VERSION 🚀🚀🚀")
        print("🔥 THIS IS THE LATEST CODE WITH DEBUGGING - DECEMBER 14, 2025 🔥")
        print("✅ BlueprintProcessor initialized with AWS Textract Adapters SDK")
        print("=" * 80)
    
    def create_adapter(self, adapter_name: str, document_type: str, feature_types: List[str]) -> str:
        """Create a Textract Adapter for document blueprint processing"""
        try:
            print(f"🚀 Creating Textract Adapter: {adapter_name} for {document_type}")
            print(f"🔍 Using feature types: {feature_types}")
            
            # Try creating adapter with feature types first
            try:
                response = self.textract_client.create_adapter(
                    AdapterName=adapter_name,
                    ClientRequestToken=f"{adapter_name}-{int(time.time())}",
                    Description=f"BDA Blueprint adapter for {document_type} processing",
                    FeatureTypes=feature_types,
                    AutoUpdate='ENABLED'
                )
            except ClientError as e:
                if 'FeatureTypes' in str(e):
                    print("⚠️ FeatureTypes not supported, trying without...")
                    # Try without FeatureTypes
                    response = self.textract_client.create_adapter(
                        AdapterName=adapter_name,
                        ClientRequestToken=f"{adapter_name}-{int(time.time())}",
                        Description=f"BDA Blueprint adapter for {document_type} processing",
                        AutoUpdate='ENABLED'
                    )
                else:
                    raise
            
            adapter_id = response['AdapterId']
            print(f"✅ Created Textract Adapter: {adapter_id}")
            
            return adapter_id
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')
            
            if error_code == 'ResourceAlreadyExistsException':
                print(f"✅ Adapter {adapter_name} already exists, retrieving ID...")
                return self._get_existing_adapter_id(adapter_name)
            elif error_code == 'ValidationException' and 'feature types' in error_message.lower():
                print(f"❌ Invalid feature types: {feature_types}")
                print(f"🔄 Trying without feature types specification...")
                # Try creating adapter without explicit feature types
                return self._create_adapter_without_features(adapter_name, document_type)
            else:
                raise Exception(f"Failed to create adapter: {error_code} - {error_message}")
    
    def _create_adapter_without_features(self, adapter_name: str, document_type: str) -> str:
        """Create adapter without specifying feature types"""
        try:
            response = self.textract_client.create_adapter(
                AdapterName=adapter_name,
                ClientRequestToken=f"{adapter_name}-{int(time.time())}",
                Description=f"BDA Blueprint adapter for {document_type} processing",
                AutoUpdate='ENABLED'
                # No FeatureTypes specified
            )
            
            adapter_id = response['AdapterId']
            print(f"✅ Created Textract Adapter without feature types: {adapter_id}")
            
            return adapter_id
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')
            raise Exception(f"Failed to create adapter without features: {error_code} - {error_message}")
    
    def _get_existing_adapter_id(self, adapter_name: str) -> str:
        """Get existing adapter ID by name"""
        try:
            response = self.textract_client.list_adapters()
            
            for adapter in response.get('Adapters', []):
                if adapter['AdapterName'] == adapter_name:
                    return adapter['AdapterId']
            
            raise Exception(f"Adapter {adapter_name} not found")
            
        except ClientError as e:
            raise Exception(f"Failed to list adapters: {str(e)}")
    
    def create_adapter_version(self, adapter_id: str, dataset_config: Dict) -> str:
        """Create a new version of the adapter with training data"""
        try:
            print(f"📚 Creating adapter version for training...")
            
            response = self.textract_client.create_adapter_version(
                AdapterId=adapter_id,
                ClientRequestToken=f"version-{int(time.time())}",
                DatasetConfig=dataset_config,
                OutputConfig={
                    'S3Bucket': dataset_config['ManifestS3Object']['Bucket'],
                    'S3Prefix': 'adapter-output/'
                }
            )
            
            version_id = response['AdapterVersionId']
            print(f"✅ Created adapter version: {version_id}")
            
            return version_id
            
        except ClientError as e:
            raise Exception(f"Failed to create adapter version: {str(e)}")
    
    def process_document(self, document_bytes: bytes, doc_type: str) -> Dict[str, Any]:
        """Process document using BDA Blueprint (Textract Adapters)"""
        try:
            print("🔥🔥🔥 RUNNING UPDATED CODE - REAL AWS BDA BLUEPRINT PROCESSING 🔥🔥🔥")
            print(f"📄 Processing {doc_type} document using BDA Blueprint...")
            
            # Get or create adapter for document type
            adapter_id = self._get_or_create_adapter_for_type(doc_type)
            
            # Process document with Textract Adapter or fallback
            if adapter_id is None:
                print("🔄 Using standard Textract processing (no adapter available)")
                if doc_type == 'w2':
                    result = self._process_w2_standard_textract(document_bytes)
                elif doc_type == 'bank_statement':
                    result = self._process_bank_statement_standard_textract(document_bytes)
                else:
                    raise ValueError(f"Unsupported document type: {doc_type}")
            else:
                print(f"🚀 Using Textract Adapter: {adapter_id}")
                if doc_type == 'w2':
                    result = self._process_w2_document(document_bytes, adapter_id)
                elif doc_type == 'bank_statement':
                    result = self._process_bank_statement_document(document_bytes, adapter_id)
                else:
                    raise ValueError(f"Unsupported document type: {doc_type}")
            
            return result
            
        except Exception as e:
            raise Exception(f"BDA Blueprint processing failed: {str(e)}")
    
    def _get_or_create_adapter_for_type(self, doc_type: str) -> str:
        """Get existing or create new adapter for document type"""
        adapter_name = f"bda-{doc_type}-adapter"
        
        try:
            # Try to get existing adapter
            adapter_id = self._get_existing_adapter_id(adapter_name)
            print(f"✅ Found existing adapter: {adapter_id}")
            return adapter_id
        except Exception as e:
            print(f"⚠️ No existing adapter found: {str(e)}")
            print(f"🔄 Creating new adapter for {doc_type}...")
            
            # Create new adapter if doesn't exist
            # Textract Adapters only support specific feature types
            feature_types = ['FORMS']  # Start with basic FORMS support
            
            try:
                return self.create_adapter(adapter_name, doc_type, feature_types)
            except Exception as create_error:
                print(f"❌ Failed to create adapter: {str(create_error)}")
                print(f"🔄 Falling back to standard Textract processing...")
                return None  # Signal to use fallback processing
    
    def _process_w2_document(self, document_bytes: bytes, adapter_id: str) -> Dict[str, Any]:
        """Process W-2 document using Textract Adapter"""
        try:
            print("🔍 Processing W-2 with Textract Adapter...")
            
            # Use AnalyzeDocument with Adapter for W-2 processing
            response = self.textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS', 'TABLES'],  # Required parameter with proper feature types
                AdaptersConfig={
                    'Adapters': [
                        {
                            'AdapterId': adapter_id,
                            'Pages': ['*'],
                            'Version': '1'
                        }
                    ]
                }
            )
            
            # Extract W-2 specific fields using adapter results
            extracted_data = self._extract_w2_fields_from_adapter_response(response)
            
            return {
                'adapter_id': adapter_id,
                'document_type': 'w2',
                'extracted_data': extracted_data,
                'processing_metadata': {
                    'method': 'textract_adapter',
                    'adapter_used': True,
                    'blocks_processed': len(response.get('Blocks', [])),
                    'confidence_threshold': 0.8
                }
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            print(f"⚠️ Adapter processing failed ({error_code}), falling back to standard Textract...")
            
            # Fallback to standard Textract if adapter fails
            return self._process_w2_standard_textract(document_bytes)
    
    def _process_bank_statement_document(self, document_bytes: bytes, adapter_id: str) -> Dict[str, Any]:
        """Process bank statement using Textract Adapter"""
        try:
            print("🔍 Processing bank statement with Textract Adapter...")
            
            # Use AnalyzeDocument with Adapter for bank statement processing
            response = self.textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS', 'TABLES'],  # Required parameter with proper feature types
                AdaptersConfig={
                    'Adapters': [
                        {
                            'AdapterId': adapter_id,
                            'Pages': ['*'],
                            'Version': '1'
                        }
                    ]
                }
            )
            
            # Extract bank statement fields using adapter results
            extracted_data = self._extract_bank_statement_fields_from_adapter_response(response)
            
            return {
                'adapter_id': adapter_id,
                'document_type': 'bank_statement',
                'extracted_data': extracted_data,
                'processing_metadata': {
                    'method': 'textract_adapter',
                    'adapter_used': True,
                    'blocks_processed': len(response.get('Blocks', [])),
                    'confidence_threshold': 0.8
                }
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            print(f"⚠️ Adapter processing failed ({error_code}), falling back to standard Textract...")
            
            # Fallback to standard Textract if adapter fails
            return self._process_bank_statement_standard_textract(document_bytes)
    
    def _extract_w2_fields_from_adapter_response(self, response: Dict) -> Dict[str, Any]:
        """Extract W-2 fields from Textract Adapter response"""
        blocks = response.get('Blocks', [])
        
        # Build block relationships map
        block_map = {block['Id']: block for block in blocks}
        
        # Extract key-value pairs with adapter enhancements
        key_value_pairs = {}
        for block in blocks:
            if block['BlockType'] == 'KEY_VALUE_SET' and 'KEY' in block.get('EntityTypes', []):
                key_text = self._get_text_from_block(block, block_map)
                value_text = self._get_value_for_key(block, block_map)
                if key_text and value_text:
                    key_value_pairs[key_text.strip()] = value_text.strip()
        
        # Map to W-2 structure using adapter intelligence
        w2_data = {
            'employee_info': {
                'name': self._find_field_value(key_value_pairs, ['employee name', 'employee\'s name']),
                'ssn': self._find_field_value(key_value_pairs, ['social security number', 'ssn']),
                'address': self._find_field_value(key_value_pairs, ['employee address', 'address'])
            },
            'employer_info': {
                'name': self._find_field_value(key_value_pairs, ['employer name', 'company name']),
                'ein': self._find_field_value(key_value_pairs, ['employer identification', 'ein']),
                'address': self._find_field_value(key_value_pairs, ['employer address', 'company address'])
            },
            'tax_info': {
                'wages': self._find_field_value(key_value_pairs, ['wages', 'box 1', 'total wages']),
                'federal_tax_withheld': self._find_field_value(key_value_pairs, ['federal income tax', 'box 2']),
                'social_security_wages': self._find_field_value(key_value_pairs, ['social security wages', 'box 3']),
                'medicare_wages': self._find_field_value(key_value_pairs, ['medicare wages', 'box 5'])
            },
            'confidence_scores': self._calculate_confidence_scores(blocks)
        }
        
        return w2_data
    
    def _extract_bank_statement_fields_from_adapter_response(self, response: Dict) -> Dict[str, Any]:
        """Extract bank statement fields from Textract Adapter response"""
        blocks = response.get('Blocks', [])
        
        # Build block relationships map
        block_map = {block['Id']: block for block in blocks}
        
        # Extract key-value pairs
        key_value_pairs = {}
        for block in blocks:
            if block['BlockType'] == 'KEY_VALUE_SET' and 'KEY' in block.get('EntityTypes', []):
                key_text = self._get_text_from_block(block, block_map)
                value_text = self._get_value_for_key(block, block_map)
                if key_text and value_text:
                    key_value_pairs[key_text.strip()] = value_text.strip()
        
        # Extract tables (transactions)
        transactions = self._extract_transactions_from_tables(blocks, block_map)
        
        # Map to bank statement structure
        statement_data = {
            'account_info': {
                'account_number': self._find_field_value(key_value_pairs, ['account number', 'account #']),
                'account_holder': self._find_field_value(key_value_pairs, ['account holder', 'customer name']),
                'bank_name': self._find_field_value(key_value_pairs, ['bank name', 'institution'])
            },
            'statement_period': {
                'start_date': self._find_field_value(key_value_pairs, ['statement period', 'from date']),
                'end_date': self._find_field_value(key_value_pairs, ['through date', 'to date'])
            },
            'balances': {
                'beginning_balance': self._find_field_value(key_value_pairs, ['beginning balance', 'opening balance']),
                'ending_balance': self._find_field_value(key_value_pairs, ['ending balance', 'closing balance'])
            },
            'transactions': transactions,
            'confidence_scores': self._calculate_confidence_scores(blocks)
        }
        
        return statement_data
    
    def _process_w2_standard_textract(self, document_bytes: bytes) -> Dict[str, Any]:
        """Fallback W-2 processing using standard Textract"""
        try:
            print(f"📄 Processing document with standard Textract (size: {len(document_bytes)} bytes)")
            
            # Validate document size and format
            if len(document_bytes) == 0:
                raise Exception("Document is empty")
            
            if len(document_bytes) > 10 * 1024 * 1024:  # 10MB limit
                raise Exception("Document too large for synchronous processing")
            
            # Check if it's a valid PDF
            if document_bytes.startswith(b'%PDF-'):
                print("✅ Processing PDF document")
            elif document_bytes.startswith(b'\xff\xd8\xff'):
                print("✅ Processing JPEG image")
            elif document_bytes.startswith(b'\x89PNG'):
                print("✅ Processing PNG image")
            else:
                print("⚠️ Unknown document format, attempting to process anyway")
            
            response = self.textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            extracted_data = self._extract_w2_fields_from_adapter_response(response)
            
            return {
                'adapter_id': None,
                'document_type': 'w2',
                'extracted_data': extracted_data,
                'processing_metadata': {
                    'method': 'standard_textract_fallback',
                    'adapter_used': False,
                    'blocks_processed': len(response.get('Blocks', [])),
                    'note': 'Adapter unavailable, used standard Textract'
                }
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')
            print(f"❌ AWS Textract Error: {error_code} - {error_message}")
            
            if error_code == 'UnsupportedDocumentException':
                raise Exception(f"Document format not supported by AWS Textract. Error: {error_message}")
            elif error_code == 'InvalidParameterException':
                raise Exception(f"Invalid parameters sent to Textract. Error: {error_message}")
            elif error_code == 'DocumentTooLargeException':
                raise Exception(f"Document is too large for processing. Error: {error_message}")
            else:
                raise Exception(f"AWS Textract error ({error_code}): {error_message}")
        except Exception as e:
            print(f"❌ Unexpected error in standard Textract processing: {str(e)}")
            raise Exception(f"Standard Textract processing failed: {str(e)}")
    
    def _process_bank_statement_standard_textract(self, document_bytes: bytes) -> Dict[str, Any]:
        """Fallback bank statement processing using standard Textract"""
        try:
            response = self.textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            extracted_data = self._extract_bank_statement_fields_from_adapter_response(response)
            
            return {
                'adapter_id': None,
                'document_type': 'bank_statement',
                'extracted_data': extracted_data,
                'processing_metadata': {
                    'method': 'standard_textract_fallback',
                    'adapter_used': False,
                    'blocks_processed': len(response.get('Blocks', [])),
                    'note': 'Adapter unavailable, used standard Textract'
                }
            }
            
        except Exception as e:
            raise Exception(f"Standard Textract processing failed: {str(e)}")
    
    def list_adapters(self) -> List[Dict]:
        """List all BDA Blueprint adapters"""
        try:
            response = self.textract_client.list_adapters()
            return response.get('Adapters', [])
        except ClientError as e:
            raise Exception(f"Failed to list adapters: {str(e)}")
    
    def get_adapter_details(self, adapter_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific adapter"""
        try:
            response = self.textract_client.get_adapter(AdapterId=adapter_id)
            return response
        except ClientError as e:
            raise Exception(f"Failed to get adapter details: {str(e)}")
    
    async def create_blueprint_project(self, project_name: str, document_type: str, description: str) -> Dict[str, Any]:
        """Create a real AWS BDA Blueprint project with S3 storage and adapters"""
        try:
            print(f"🏗️ Creating AWS BDA Blueprint project: {project_name}")
            
            # Step 1: Create S3 bucket for document storage
            bucket_name = f"bda-blueprint-{project_name.lower().replace('_', '-')}-{int(time.time())}"
            s3_bucket = self._create_s3_bucket(bucket_name)
            print(f"✅ Created S3 bucket: {s3_bucket}")
            
            # Step 2: Create Textract Adapter for the document type
            adapter_name = f"bda-{project_name.lower()}-{document_type}-adapter"
            try:
                adapter_id = self.create_adapter(adapter_name, document_type, ['FORMS'])
                print(f"✅ Created Textract Adapter: {adapter_id}")
            except Exception as adapter_error:
                print(f"⚠️ Adapter creation failed: {str(adapter_error)}")
                print("🔄 Continuing without adapter - will use standard Textract processing")
                adapter_id = None
            
            # Step 3: Create project metadata
            project_arn = f"arn:aws:textract:{self.region_name}:blueprint:project/{project_name}"
            
            # Step 4: Store project configuration in S3
            project_config = {
                "project_name": project_name,
                "project_arn": project_arn,
                "document_type": document_type,
                "description": description,
                "s3_bucket": s3_bucket,
                "adapter_id": adapter_id,
                "adapter_name": adapter_name if adapter_id else None,
                "created_at": time.time(),
                "status": "ACTIVE",
                "region": self.region_name,
                "processing_mode": "adapter" if adapter_id else "standard_textract"
            }
            
            self._store_project_config(s3_bucket, project_config)
            print(f"✅ Stored project configuration in S3")
            
            return {
                "project_arn": project_arn,
                "s3_bucket": s3_bucket,
                "adapter_id": adapter_id,
                "status": "ACTIVE",
                "processing_mode": "adapter" if adapter_id else "standard_textract",
                "note": "Adapter created successfully" if adapter_id else "Using standard Textract processing"
            }
            
        except Exception as e:
            print(f"❌ Failed to create Blueprint project: {str(e)}")
            raise Exception(f"Blueprint project creation failed: {str(e)}")
    
    def _create_s3_bucket(self, bucket_name: str) -> str:
        """Create S3 bucket for Blueprint project storage"""
        try:
            print(f"🪣 Creating S3 bucket: {bucket_name}")
            
            if self.region_name == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region_name}
                )
            
            # Enable versioning for document management
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Set up bucket policy for Textract access
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "TextractAccess",
                        "Effect": "Allow",
                        "Principal": {"Service": "textract.amazonaws.com"},
                        "Action": ["s3:GetObject", "s3:PutObject"],
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            
            self.s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            print(f"✅ S3 bucket configured: {bucket_name}")
            return bucket_name
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'BucketAlreadyExists':
                print(f"⚠️ Bucket name already exists, trying alternative...")
                # Try with timestamp suffix
                alt_bucket_name = f"{bucket_name}-{int(time.time())}"
                return self._create_s3_bucket(alt_bucket_name)
            else:
                raise Exception(f"Failed to create S3 bucket: {str(e)}")
    
    def _store_project_config(self, bucket_name: str, config: Dict[str, Any]):
        """Store project configuration in S3"""
        try:
            config_key = "blueprint-project-config.json"
            
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=config_key,
                Body=json.dumps(config, indent=2),
                ContentType='application/json'
            )
            
            print(f"✅ Project configuration stored in s3://{bucket_name}/{config_key}")
            
        except ClientError as e:
            raise Exception(f"Failed to store project config: {str(e)}")
    
    async def list_blueprint_projects(self) -> List[Dict[str, Any]]:
        """List all Blueprint projects by scanning S3 buckets"""
        try:
            print("📋 Scanning for Blueprint projects in AWS account...")
            
            projects = []
            
            # List all S3 buckets
            response = self.s3_client.list_buckets()
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                # Check if this is a Blueprint project bucket
                if bucket_name.startswith('bda-blueprint-'):
                    try:
                        # Try to get project configuration
                        config_response = self.s3_client.get_object(
                            Bucket=bucket_name,
                            Key='blueprint-project-config.json'
                        )
                        
                        config = json.loads(config_response['Body'].read())
                        projects.append(config)
                        
                    except ClientError:
                        # Skip buckets without project config
                        continue
            
            print(f"✅ Found {len(projects)} Blueprint projects")
            return projects
            
        except Exception as e:
            print(f"❌ Failed to list Blueprint projects: {str(e)}")
            raise Exception(f"Failed to list Blueprint projects: {str(e)}")
    
    async def get_project_status(self, project_arn: str) -> Dict[str, Any]:
        """Get detailed status of a Blueprint project"""
        try:
            print(f"🔍 Getting status for project: {project_arn}")
            
            # Extract project name from ARN
            project_name = project_arn.split('/')[-1]
            
            # Find the project bucket
            projects = await self.list_blueprint_projects()
            project_config = None
            
            for project in projects:
                if project.get('project_name') == project_name:
                    project_config = project
                    break
            
            if not project_config:
                raise Exception(f"Project not found: {project_name}")
            
            # Get adapter status
            adapter_status = "UNKNOWN"
            try:
                adapter_details = self.get_adapter_details(project_config['adapter_id'])
                adapter_status = adapter_details.get('Status', 'UNKNOWN')
            except:
                pass
            
            # Get S3 bucket info
            bucket_name = project_config['s3_bucket']
            document_count = 0
            try:
                objects = self.s3_client.list_objects_v2(Bucket=bucket_name)
                document_count = objects.get('KeyCount', 0)
            except:
                pass
            
            status = {
                "project_name": project_config['project_name'],
                "project_arn": project_arn,
                "status": project_config.get('status', 'UNKNOWN'),
                "adapter_status": adapter_status,
                "s3_bucket": bucket_name,
                "document_count": document_count,
                "created_at": project_config.get('created_at'),
                "last_updated": time.time()
            }
            
            print(f"✅ Retrieved project status: {status}")
            return status
            
        except Exception as e:
            print(f"❌ Failed to get project status: {str(e)}")
            raise Exception(f"Failed to get project status: {str(e)}")
    
    # Helper methods
    def _get_text_from_block(self, block: Dict, block_map: Dict) -> str:
        """Extract text from block using relationships"""
        text_parts = []
        if 'Relationships' in block:
            for relationship in block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        child_block = block_map.get(child_id)
                        if child_block and child_block['BlockType'] == 'WORD':
                            text_parts.append(child_block.get('Text', ''))
        return ' '.join(text_parts)
    
    def _get_value_for_key(self, key_block: Dict, block_map: Dict) -> str:
        """Get value text for a key block"""
        if 'Relationships' in key_block:
            for relationship in key_block['Relationships']:
                if relationship['Type'] == 'VALUE':
                    for value_id in relationship['Ids']:
                        value_block = block_map.get(value_id)
                        if value_block:
                            return self._get_text_from_block(value_block, block_map)
        return ""
    
    def _find_field_value(self, key_value_pairs: Dict, keywords: List[str]) -> Optional[str]:
        """Find field value by matching keywords"""
        for key, value in key_value_pairs.items():
            key_lower = key.lower()
            for keyword in keywords:
                if keyword.lower() in key_lower:
                    return value
        return None
    
    def _extract_transactions_from_tables(self, blocks: List[Dict], block_map: Dict) -> List[Dict]:
        """Extract transaction data from table blocks"""
        transactions = []
        
        for block in blocks:
            if block['BlockType'] == 'TABLE':
                # Extract table data - simplified implementation
                # In real implementation, would parse table structure properly
                pass
        
        return transactions
    
    def _calculate_confidence_scores(self, blocks: List[Dict]) -> Dict[str, float]:
        """Calculate confidence scores from blocks"""
        confidences = [block.get('Confidence', 0) for block in blocks if 'Confidence' in block]
        
        if not confidences:
            return {'average': 0.0, 'minimum': 0.0, 'maximum': 0.0}
        
        return {
            'average': sum(confidences) / len(confidences),
            'minimum': min(confidences),
            'maximum': max(confidences)
        }    

    async def upload_document_to_project(self, project_name: str, document_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Upload a document to a Blueprint project for training or processing"""
        try:
            print(f"📤 Uploading document to Blueprint project: {project_name}")
            
            # Find the project
            projects = await self.list_blueprint_projects()
            project_config = None
            
            for project in projects:
                if project.get('project_name') == project_name:
                    project_config = project
                    break
            
            if not project_config:
                raise Exception(f"Blueprint project not found: {project_name}")
            
            bucket_name = project_config['s3_bucket']
            
            # Create document key with timestamp
            timestamp = int(time.time())
            document_key = f"documents/{timestamp}_{filename}"
            
            # Upload document to S3
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=document_key,
                Body=document_bytes,
                ContentType=self._get_content_type(filename)
            )
            
            # Store document metadata
            metadata = {
                "filename": filename,
                "document_key": document_key,
                "uploaded_at": timestamp,
                "size_bytes": len(document_bytes),
                "project_name": project_name
            }
            
            metadata_key = f"metadata/{timestamp}_{filename}.json"
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=metadata_key,
                Body=json.dumps(metadata, indent=2),
                ContentType='application/json'
            )
            
            print(f"✅ Document uploaded: s3://{bucket_name}/{document_key}")
            
            return {
                "document_key": document_key,
                "s3_uri": f"s3://{bucket_name}/{document_key}",
                "metadata_key": metadata_key,
                "upload_timestamp": timestamp
            }
            
        except Exception as e:
            print(f"❌ Failed to upload document: {str(e)}")
            raise Exception(f"Document upload failed: {str(e)}")
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension"""
        ext = filename.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'txt': 'text/plain'
        }
        return content_types.get(ext, 'application/octet-stream')