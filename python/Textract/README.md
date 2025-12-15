# Textract Project

This project demonstrates BDA using AWS Textract service directly for document analysis of W-2 forms and bank statements.

## Overview
- **Pattern**: Direct AWS Textract API calls with custom parsing
- **Language**: Python
- **Deployment**: AWS Lambda + S3 triggers
- **Documents**: W-2 forms, Bank statements

## Architecture
```
S3 Upload → Lambda Trigger → Textract API → Custom Parser → Results
```

## Features
- Direct Textract API integration
- Custom field extraction logic
- S3-based document processing
- Asynchronous processing for large documents
- Custom confidence scoring

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure S3 bucket and Lambda triggers
3. Deploy using: `python deploy.py`

## Processing Flow
1. Upload document to S3 bucket
2. Lambda function triggered automatically
3. Textract processes document
4. Custom parser extracts relevant fields
5. Results stored in DynamoDB