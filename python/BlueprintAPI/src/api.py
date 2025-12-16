"""
FastAPI application for Blueprint-based document processing
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import sys
import os

# Add shared utilities to path
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared')
sys.path.append(shared_path)

try:
    from .blueprint_processor import BlueprintProcessor
except ImportError:
    # Fallback for direct execution
    from blueprint_processor import BlueprintProcessor

# Import document validator with error handling
try:
    from utils.document_validator import DocumentValidator
    validator = DocumentValidator()
except ImportError:
    print("⚠️  Document validator not available - using basic validation")
    validator = None

print("=" * 80)
print("🔥🔥🔥 FASTAPI STARTING - UPDATED CODE VERSION 3.0 - DEC 14, 2025 🔥🔥🔥")
print("🚀 This is the LATEST API code with debugging!")
print("=" * 80)

app = FastAPI(title="Blueprint API Document Processor", version="3.0.0")

print("📡 Creating BlueprintProcessor instance...")
processor = BlueprintProcessor()
print("✅ BlueprintProcessor created successfully!")

@app.get("/")
async def root():
    """Root endpoint to verify API is running latest code"""
    return {
        "message": "🔥 Blueprint API v3.0 - UPDATED CODE RUNNING - Dec 14, 2025 🔥",
        "status": "running",
        "version": "3.0.0",
        "debug": "This is the LATEST code with debugging!"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with version info"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": "2025-12-14",
        "message": "🚀 Latest Blueprint API code is running!"
    }

@app.post("/process/w2")
async def process_w2(file: UploadFile = File(...)):
    """Process W-2 document using real Blueprint API"""
    try:
        # Check file format
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}. Supported: JPEG, PNG, PDF"
            )
        # Read file content
        content = await file.read()
        
        # Validation
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        if not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="Only PDF and image files are supported")
        
        # Additional PDF validation and size check
        print(f"📄 Processing file: {file.filename}")
        print(f"📊 File size: {len(content)} bytes")
        print(f"🏷️ Content type: {file.content_type}")
        
        # AWS Textract limits: 10MB for synchronous, 500MB for asynchronous
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB for synchronous processing")
        
        # Validate PDF header if it's a PDF
        if file.filename.lower().endswith('.pdf'):
            if not content.startswith(b'%PDF-'):
                raise HTTPException(status_code=400, detail="Invalid PDF file format")
            print("✅ Valid PDF header detected")
            
            # Try PDF-to-image conversion for better Textract compatibility
            try:
                import fitz  # PyMuPDF
                print("🔄 Converting PDF to image for better Textract compatibility...")
                
                # Open PDF with PyMuPDF
                pdf_doc = fitz.open(stream=content, filetype="pdf")
                
                if len(pdf_doc) == 0:
                    raise HTTPException(status_code=400, detail="PDF has no pages")
                
                # Convert first page to image
                page = pdf_doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
                pdf_doc.close()
                
                print(f"✅ PDF converted to PNG image ({len(img_data)} bytes)")
                content = img_data  # Use converted image instead of original PDF
                
            except ImportError:
                print("⚠️ PyMuPDF not available, trying alternative PDF processing...")
                # Try alternative approach with pdf2image if available
                try:
                    from pdf2image import convert_from_bytes
                    print("🔄 Using pdf2image for PDF conversion...")
                    
                    images = convert_from_bytes(content, first_page=1, last_page=1, dpi=200)
                    if images:
                        import io
                        img_buffer = io.BytesIO()
                        images[0].save(img_buffer, format='PNG')
                        content = img_buffer.getvalue()
                        print(f"✅ PDF converted to PNG using pdf2image ({len(content)} bytes)")
                    
                except ImportError:
                    print("⚠️ pdf2image not available, trying PDF directly with Textract")
                except Exception as e:
                    print(f"⚠️ pdf2image conversion failed: {str(e)}, trying PDF directly")
            except Exception as e:
                print(f"⚠️ PDF conversion failed: {str(e)}, trying PDF directly with Textract")
        
        # Process document with Blueprint
        print("🚀 Sending to BlueprintProcessor...")
        result = processor.process_document(content, 'w2')
        
        return JSONResponse(content={
            "status": "success",
            "document_type": "w2",
            "blueprint_result": result,
            "filename": file.filename,
            "message": "Document processed using real AWS Blueprint API"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blueprint processing failed: {str(e)}")

@app.post("/process/bank-statement")
async def process_bank_statement(file: UploadFile = File(...)):
    """Process bank statement using real Blueprint API"""
    try:
        # Read file content
        content = await file.read()
        
        # Validation
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        if not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="Only PDF and image files are supported")
        
        # Process document with Blueprint
        result = processor.process_document(content, 'bank_statement')
        
        return JSONResponse(content={
            "status": "success",
            "document_type": "bank_statement",
            "blueprint_result": result,
            "filename": file.filename,
            "message": "Document processed using real AWS Blueprint API"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blueprint processing failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Blueprint API Document Processor",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "w2_processing": "/process/w2",
            "bank_statement_processing": "/process/bank-statement"
        },
        "usage": "Go to /docs for interactive API documentation"
    }

@app.post("/blueprint/create")
async def create_blueprint_project(project_name: str, document_type: str = "w2", description: str = "BDA Blueprint project"):
    """Create a new Blueprint project programmatically"""
    try:
        result = await processor.create_blueprint_project(project_name, document_type, description)
        return {
            "status": "success",
            "project_arn": result["project_arn"],
            "s3_bucket": result["s3_bucket"],
            "adapter_id": result["adapter_id"],
            "project_name": project_name,
            "document_type": document_type,
            "message": f"Blueprint project '{project_name}' created in your AWS account with S3 bucket and Textract Adapter"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blueprint/projects")
async def list_blueprint_projects():
    """List all Blueprint projects"""
    try:
        projects = await processor.list_blueprint_projects()
        return {
            "status": "success",
            "projects": projects,
            "count": len(projects),
            "message": f"Found {len(projects)} Blueprint projects in your AWS account"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blueprint/project/{project_name}/status")
async def get_project_status(project_name: str):
    """Get comprehensive status of a BDA project including documents and fields"""
    try:
        status = await processor.get_comprehensive_project_status(project_name)
        return {
            "status": "success",
            "project_status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blueprint/project/{project_name}/documents")
async def list_project_documents(project_name: str):
    """List all documents in a BDA project with metadata"""
    try:
        documents = await processor.list_project_documents(project_name)
        return {
            "status": "success",
            "project_name": project_name,
            "documents": documents,
            "document_count": len(documents),
            "message": f"Found {len(documents)} documents in project '{project_name}'"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/blueprint/project/{project_name}/fields")
async def get_project_fields(project_name: str):
    """Get extracted fields and schema for a BDA project"""
    try:
        fields = await processor.get_project_fields(project_name)
        return {
            "status": "success",
            "project_name": project_name,
            "fields": fields
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/blueprint/project/{project_name}/upload")
async def upload_document_to_project(project_name: str, file: UploadFile = File(...)):
    """Upload a document to a Blueprint project for training or processing - stores in AWS S3"""
    try:
        print(f"📤 Uploading document to Blueprint project: {project_name}")
        
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Upload to Blueprint project
        result = await processor.upload_document_to_project(
            project_name=project_name,
            document_bytes=content,
            filename=file.filename
        )
        
        return JSONResponse(content={
            "status": "success",
            "project_name": project_name,
            "filename": file.filename,
            "s3_uri": result.get("s3_uri") or result.get("document_s3_uri"),
            "document_key": result.get("document_key"),
            "upload_timestamp": result.get("upload_timestamp"),
            "invocation_arn": result.get("invocation_arn"),
            "service": result.get("service"),
            "message": f"Document uploaded to Blueprint project '{project_name}' in your AWS account"
        })
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "blueprint-api", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting Blueprint API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)