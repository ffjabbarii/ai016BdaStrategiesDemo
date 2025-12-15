"""
Common document validation utilities for BDA projects
"""
import json
import os
from typing import Dict, List, Optional

class DocumentValidator:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'aws-config.json')
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def validate_document_type(self, file_path: str, doc_type: str) -> Dict[str, bool]:
        """Validate document against type requirements"""
        result = {
            'valid': True,
            'errors': []
        }
        
        if doc_type not in self.config['document_types']:
            result['valid'] = False
            result['errors'].append(f"Unknown document type: {doc_type}")
            return result
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        max_size = self.config['document_types'][doc_type]['max_size_mb']
        
        if file_size_mb > max_size:
            result['valid'] = False
            result['errors'].append(f"File size {file_size_mb:.2f}MB exceeds limit of {max_size}MB")
        
        return result
    
    def get_supported_formats(self, doc_type: str) -> List[str]:
        """Get supported MIME types for document type"""
        return self.config['document_types'].get(doc_type, {}).get('mime_types', [])