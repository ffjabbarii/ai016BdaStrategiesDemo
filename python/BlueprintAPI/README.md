# BlueprintAPI Project

This project demonstrates BDA using AWS Blueprint API programmatically to extract structured data from W-2 forms and bank statements.

## Overview
- **Pattern**: AWS Blueprint API with custom processing pipeline
- **Language**: Python
- **Deployment**: AWS Lambda + API Gateway
- **Documents**: W-2 forms, Bank statements

## Architecture
```
Client → API Gateway → Lambda → Blueprint API → Response
```

## Features
- Automated document classification
- Structured data extraction using Blueprint templates
- RESTful API for document processing
- Batch processing capabilities
- Error handling and validation

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure AWS credentials
3. Deploy using: `python deploy.py`

## API Endpoints
- `POST /process/w2` - Process W-2 document
- `POST /process/bank-statement` - Process bank statement
- `GET /status/{job_id}` - Check processing status