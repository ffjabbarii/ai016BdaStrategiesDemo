# AnalyzeDocument Project (C#)

This project demonstrates advanced BDA using Textract SDK's AnalyzeDocument feature with enhanced capabilities for W-2 forms and bank statements using C# and .NET.

## Overview
- **Pattern**: Textract SDK AnalyzeDocument with advanced features
- **Language**: C# (.NET 6)
- **Framework**: ASP.NET Core Web API
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
- Image preprocessing with ImageSharp and OpenCV

## Setup
1. Install .NET 6 SDK
2. Restore dependencies: `dotnet restore`
3. Run locally: `dotnet run`
4. Build Docker container: `docker build -t analyze-document-csharp .`
5. Deploy to ECS using AWS CLI or CDK

## Advanced Features
- Document layout analysis
- Signature detection
- Enhanced image preprocessing
- Multi-page document support
- Custom field extraction rules
- Statistical confidence analysis

## API Endpoints
- `POST /api/document/analyze/w2` - Analyze W-2 document
- `POST /api/document/analyze/bank-statement` - Analyze bank statement
- `GET /api/document/health` - Health check endpoint

## Project Structure
```
AnalyzeDocument/
├── Controllers/         # API controllers
├── Services/           # Business logic services
├── Models/             # Data models and DTOs
├── Program.cs          # Application entry point
└── AnalyzeDocument.csproj # Project file with dependencies
```