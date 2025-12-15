# Textract Project (C#)

This project demonstrates BDA using AWS Textract service directly with .NET Lambda functions for document analysis of W-2 forms and bank statements.

## Overview
- **Pattern**: Direct AWS Textract API calls with custom parsing
- **Language**: C# (.NET 6)
- **Framework**: AWS Lambda Functions
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
- Strongly typed models

## Setup
1. Install .NET 6 SDK
2. Install AWS Lambda Tools: `dotnet tool install -g Amazon.Lambda.Tools`
3. Restore dependencies: `dotnet restore`
4. Configure S3 bucket and Lambda triggers
5. Deploy using: `dotnet lambda deploy-function`

## Processing Flow
1. Upload document to S3 bucket
2. Lambda function triggered automatically
3. Textract processes document
4. Custom parser extracts relevant fields
5. Results stored in DynamoDB

## Project Structure
```
Textract/
├── Services/            # Business logic services
├── Models/              # Data models and DTOs
├── Function.cs          # Lambda entry point
└── Textract.csproj      # Project file with dependencies
```