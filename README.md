# BDA Strategies Demo

This repository demonstrates three different approaches to Business Document Analysis (BDA) using AWS services, implemented in both **Python** and **C#**. Each project processes W-2 forms and bank statements using different patterns and AWS services.

## Language Implementations

### Python Implementation (`./python/`)
- **Framework**: FastAPI, AWS Lambda
- **Dependencies**: boto3, OpenCV, Pillow
- **Deployment**: Lambda functions, containerized services

### C# Implementation (`./csharp/`)
- **Framework**: ASP.NET Core, AWS Lambda
- **Dependencies**: AWS SDK for .NET, OpenCvSharp, ImageSharp
- **Deployment**: Lambda functions, containerized services

## BDA Patterns

### 1. BlueprintAPI
Uses AWS Blueprint API programmatically to extract data from documents.
- **Python**: `./python/BlueprintAPI/`
- **C#**: `./csharp/BlueprintAPI/`
- **Pattern**: Blueprint API with custom processing
- **Documents**: W-2 forms, Bank statements

### 2. Textract
Direct implementation using AWS Textract service for document analysis.
- **Python**: `./python/Textract/`
- **C#**: `./csharp/Textract/`
- **Pattern**: AWS Textract direct API calls
- **Documents**: W-2 forms, Bank statements

### 3. AnalyzeDocument
Advanced document analysis using Textract SDK's AnalyzeDocument feature.
- **Python**: `./python/AnalyzeDocument/`
- **C#**: `./csharp/AnalyzeDocument/`
- **Pattern**: Textract SDK AnalyzeDocument with enhanced features
- **Documents**: W-2 forms, Bank statements

## Shared Resources
- **Location**: `./shared/`
- **Contents**: Sample documents, common utilities, configuration files

## Getting Started

Each project has its own README with specific setup and deployment instructions. Navigate to the respective language and project directory to begin.

### Python Prerequisites
- AWS CLI configured
- Python 3.8+
- pip for package management
- AWS account with appropriate permissions

### C# Prerequisites
- AWS CLI configured
- .NET 6.0 or later
- Visual Studio or VS Code
- AWS account with appropriate permissions

## Comparison Benefits

This dual-language approach allows you to:
- Compare implementation patterns between Python and C#
- Evaluate performance differences
- Choose the best language for your team's expertise
- Use the same AWS services and sample documents across both implementations