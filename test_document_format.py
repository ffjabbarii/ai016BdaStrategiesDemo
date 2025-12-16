#!/usr/bin/env python3
"""
Test document format compatibility with Textract
"""

import boto3
from botocore.exceptions import ClientError

def test_document_format():
    """Test if our W-2 PDF is compatible with Textract"""
    
    print("🔍 Testing Document Format Compatibility")
    print("=" * 50)
    
    # Initialize Textract client
    textract_client = boto3.client('textract', region_name='us-east-1')
    
    # Test the W-2 PDF file
    w2_file = "test_files/w-2.pdf"
    
    try:
        print(f"📄 Testing file: {w2_file}")
        
        # Read the PDF file
        with open(w2_file, 'rb') as f:
            document_bytes = f.read()
        
        print(f"📊 File size: {len(document_bytes)} bytes")
        
        # Check file signature
        if document_bytes.startswith(b'%PDF-'):
            print("✅ Valid PDF signature detected")
        else:
            print("❌ Invalid PDF signature")
            print(f"   First 10 bytes: {document_bytes[:10]}")
        
        # Test 1: Try direct Textract processing
        print("\n🧪 Test 1: Direct Textract analyze_document...")
        try:
            response = textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            blocks = response.get('Blocks', [])
            print(f"✅ Textract processing successful!")
            print(f"   Blocks found: {len(blocks)}")
            
            # Count different block types
            block_types = {}
            for block in blocks:
                block_type = block.get('BlockType', 'UNKNOWN')
                block_types[block_type] = block_types.get(block_type, 0) + 1
            
            print(f"   Block types: {block_types}")
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_message = e.response.get('Error', {}).get('Message', '')
            print(f"❌ Textract failed: {error_code}")
            print(f"   Message: {error_message}")
            
            if error_code == 'UnsupportedDocumentException':
                print("   🎯 Issue: PDF format not supported by Textract")
                print("   💡 Solution: Convert PDF to image format")
                
                # Test 2: Try PDF to image conversion
                print("\n🧪 Test 2: PDF to image conversion...")
                try:
                    import fitz  # PyMuPDF
                    
                    # Convert PDF to PNG
                    pdf_doc = fitz.open(stream=document_bytes, filetype="pdf")
                    
                    if len(pdf_doc) == 0:
                        print("❌ PDF has no pages")
                        return
                    
                    # Convert first page to image
                    page = pdf_doc[0]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
                    png_bytes = pix.tobytes("png")
                    pdf_doc.close()
                    
                    print(f"✅ PDF converted to PNG")
                    print(f"   PNG size: {len(png_bytes)} bytes")
                    
                    # Test Textract with converted image
                    print("\n🧪 Test 3: Textract with converted PNG...")
                    try:
                        response = textract_client.analyze_document(
                            Document={'Bytes': png_bytes},
                            FeatureTypes=['FORMS', 'TABLES']
                        )
                        
                        blocks = response.get('Blocks', [])
                        print(f"✅ Textract processing successful with PNG!")
                        print(f"   Blocks found: {len(blocks)}")
                        
                        # Count different block types
                        block_types = {}
                        for block in blocks:
                            block_type = block.get('BlockType', 'UNKNOWN')
                            block_types[block_type] = block_types.get(block_type, 0) + 1
                        
                        print(f"   Block types: {block_types}")
                        
                        return True  # Success with conversion
                        
                    except ClientError as e3:
                        error_code3 = e3.response.get('Error', {}).get('Code', '')
                        error_message3 = e3.response.get('Error', {}).get('Message', '')
                        print(f"❌ Textract failed with PNG: {error_code3}")
                        print(f"   Message: {error_message3}")
                        
                except ImportError:
                    print("❌ PyMuPDF not available for PDF conversion")
                    print("   Install with: pip install PyMuPDF")
                except Exception as conv_error:
                    print(f"❌ PDF conversion failed: {str(conv_error)}")
            
            return False
        
        return True  # Success with direct PDF
        
    except FileNotFoundError:
        print(f"❌ File not found: {w2_file}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    success = test_document_format()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    
    if success:
        print("✅ Document format is compatible with Textract")
        print("   The issue may be elsewhere in the processing pipeline")
    else:
        print("❌ Document format compatibility issues found")
        print("\n🔧 RECOMMENDATIONS:")
        print("1. Ensure PyMuPDF is installed: pip install PyMuPDF")
        print("2. Check if PDF conversion is working in blueprint_processor.py")
        print("3. Verify the PDF file is not corrupted")
        print("4. Try with a different W-2 PDF file")

if __name__ == "__main__":
    main()