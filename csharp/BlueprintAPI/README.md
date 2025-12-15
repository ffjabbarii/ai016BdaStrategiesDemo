# BlueprintAPI Project (C#)

This project demonstrates BDA using AWS Blueprint API programmatically with ASP.NET Core to extract structured data from W-2 forms and bank statements.

## Overview
- **Pattern**: AWS Blueprint API with custom processing pipeline
- **Language**: C# (.NET 6)
- **Framework**: ASP.NET Core Web API
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
- Async/await pattern for better performance
- Comprehensive error handling and logging

## Setup
1. Install .NET 6 SDK
2. Restore dependencies: `dotnet restore`
3. Configure AWS credentials
4. Run locally: `dotnet run`
5. Deploy using: `dotnet lambda deploy-function`

## API Endpoints
- `POST /api/document/process/w2` - Process W-2 document
- `POST /api/document/process/bank-statement` - Process bank statement
- `GET /api/document/health` - Health check endpoint

## Project Structure
```
BlueprintAPI/
├── Controllers/          # API controllers
├── Services/            # Business logic services
├── Models/              # Data models and DTOs
├── Program.cs           # Application entry point
└── BlueprintAPI.csproj  # Project file with dependencies
```