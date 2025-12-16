#!/usr/bin/env python3
"""
Check if PyMuPDF is installed and working
"""

def check_pymupdf():
    """Check PyMuPDF installation and functionality"""
    
    print("🔍 Checking PyMuPDF Installation")
    print("=" * 40)
    
    # Test 1: Import check
    try:
        import fitz
        print("✅ PyMuPDF (fitz) imported successfully")
        print(f"   Version: {fitz.version}")
    except ImportError as e:
        print("❌ PyMuPDF not installed")
        print(f"   Error: {str(e)}")
        print("   Install with: pip install PyMuPDF")
        return False
    
    # Test 2: Basic functionality
    try:
        # Test with the W-2 PDF
        with open("test_files/w-2.pdf", 'rb') as f:
            pdf_bytes = f.read()
        
        print(f"\n📄 Testing PDF conversion...")
        print(f"   PDF size: {len(pdf_bytes)} bytes")
        
        # Open PDF
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        print(f"   Pages: {len(pdf_doc)}")
        
        if len(pdf_doc) > 0:
            # Convert first page
            page = pdf_doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            png_bytes = pix.tobytes("png")
            pdf_doc.close()
            
            print(f"✅ PDF conversion successful")
            print(f"   PNG size: {len(png_bytes)} bytes")
            
            # Save converted image for inspection
            with open("test_converted_w2.png", 'wb') as f:
                f.write(png_bytes)
            print(f"   Saved converted image: test_converted_w2.png")
            
            return True
        else:
            print("❌ PDF has no pages")
            return False
            
    except Exception as e:
        print(f"❌ PDF conversion failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_pymupdf()
    
    if success:
        print("\n✅ PyMuPDF is working correctly")
        print("   The document format issue may be elsewhere")
    else:
        print("\n❌ PyMuPDF issues found")
        print("   This could be causing the document format error")