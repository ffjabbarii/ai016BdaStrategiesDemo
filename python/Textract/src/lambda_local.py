#!/usr/bin/env python3
"""
Local development server for Textract Lambda function
Simulates Lambda execution in a local FastAPI server
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import sys
import os
import json

# Add shared utilities to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

# Import the actual processor (we'll need to create this)
try:
    from textract_processor import TextractProcessor
except ImportError:
    # Fallback if processor doesn't exist yet
    class TextractProcessor:
        def __init__(self):
            pass
        
        def process_document_sync(self, document_bytes, doc_type):
            return {
                "message": "Textract processor not fully implemented yet",
                "document_type": doc_type,
                "status": "placeholder"
            }

app = FastAPI(title="Textract Local Development Server", version="1.0.0")

processor = TextractProcessor()

@app.post("/process/w2")
async def process_w2_local(file: UploadFile = File(...)):
    """Process W-2 document locally"""
    try:
        content = await file.read()
        result = processor.process_document_sync(content, 'w2')
        
        return JSONResponse(content={
            "status": "success",
            "document_type": "w2",
            "extracted_data": result,
            "filename": file.filename,
            "mode": "local_development"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/bank-statement")
async def process_bank_statement_local(file: UploadFile = File(...)):
    """Process bank statement locally"""
    try:
        content = await file.read()
        result = processor.process_document_sync(content, 'bank_statement')
        
        return JSONResponse(content={
            "status": "success", 
            "document_type": "bank_statement",
            "extracted_data": result,
            "filename": file.filename,
            "mode": "local_development"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "textract-local", "mode": "development"}

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Textract Local Development Server",
        "endpoints": [
            "POST /process/w2",
            "POST /process/bank-statement", 
            "GET /health"
        ],
        "mode": "local_development"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)