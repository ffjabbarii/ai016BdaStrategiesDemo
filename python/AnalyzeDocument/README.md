# AnalyzeDocument Project

This project demonstrates advanced BDA using Textract SDK's AnalyzeDocument feature with enhanced capabilities for W-2 forms and bank statements.

## Overview
- **Pattern**: Textract SDK AnalyzeDocument with advanced features
- **Language**: Python
- **Deployment**: Containerized microservice on ECS
- **Documents**: W-2 forms, Bank statements

## Architecture
```
API Gateway → ECS Service → Textract AnalyzeDocument → Enhanced Parser → Response
```

## Features
- Advanced document analysis with AnalyzeDocument
- Enhanced field detection and validation
- Custom document classification
- Machine learning-based confidence scoring
- Real-time processing with caching
- Comprehensive error handling

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Build Docker container: `docker build -t analyze-document .`
3. Deploy to ECS: `python deploy.py`

## Advanced Features
- Document layout analysis
- Signature detection
- Handwriting recognition
- Multi-page document support
- Custom field extraction rules