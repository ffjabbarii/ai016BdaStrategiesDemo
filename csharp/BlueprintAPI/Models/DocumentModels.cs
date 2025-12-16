using Amazon.Textract.Model;

namespace BlueprintAPI.Models
{
    public class DocumentProcessingResult
    {
        public string DocumentType { get; set; } = string.Empty;
        public object? ExtractedData { get; set; }
        public ProcessingMetadata? ProcessingMetadata { get; set; }
        public List<Block>? RawBlocks { get; set; }
    }

    public class ProcessingMetadata
    {
        public int TotalBlocks { get; set; }
        public string ExtractionMethod { get; set; } = string.Empty;
    }

    public class W2Data
    {
        public EmployeeInfo EmployeeInfo { get; set; } = new();
        public EmployerInfo EmployerInfo { get; set; } = new();
        public TaxInfo TaxInfo { get; set; } = new();
        public ConfidenceScores ConfidenceScores { get; set; } = new();
    }

    public class EmployeeInfo
    {
        public string? Ssn { get; set; }
        public string? Name { get; set; }
        public string? Address { get; set; }
    }

    public class EmployerInfo
    {
        public string? Ein { get; set; }
        public string? Name { get; set; }
        public string? Address { get; set; }
    }

    public class TaxInfo
    {
        public decimal? Wages { get; set; }
        public decimal? FederalTaxWithheld { get; set; }
        public decimal? SocialSecurityWages { get; set; }
        public decimal? MedicareWages { get; set; }
    }

    public class BankStatementData
    {
        public AccountInfo AccountInfo { get; set; } = new();
        public List<Transaction> Transactions { get; set; } = new();
        public TransactionSummary Summary { get; set; } = new();
        public ConfidenceScores ConfidenceScores { get; set; } = new();
    }

    public class AccountInfo
    {
        public string? AccountNumber { get; set; }
        public string? RoutingNumber { get; set; }
        public string? AccountHolder { get; set; }
        public string? BankName { get; set; }
    }

    public class Transaction
    {
        public DateTime Date { get; set; }
        public string Description { get; set; } = string.Empty;
        public decimal Amount { get; set; }
        public string Type { get; set; } = string.Empty;
        public decimal Balance { get; set; }
    }

    public class TransactionSummary
    {
        public decimal TotalDeposits { get; set; }
        public decimal TotalWithdrawals { get; set; }
        public int TransactionCount { get; set; }
    }

    public class ConfidenceScores
    {
        public double Average { get; set; }
        public double Minimum { get; set; }
        public double Maximum { get; set; }
    }
} 
   public class BlueprintProjectResult
    {
        public string ProjectArn { get; set; } = string.Empty;
        public string S3Bucket { get; set; } = string.Empty;
        public string? AdapterId { get; set; }
        public string Status { get; set; } = string.Empty;
    }

    public class BlueprintProject
    {
        public string ProjectName { get; set; } = string.Empty;
        public string ProjectArn { get; set; } = string.Empty;
        public string DocumentType { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string S3Bucket { get; set; } = string.Empty;
        public string? AdapterId { get; set; }
        public double CreatedAt { get; set; }
        public string Status { get; set; } = string.Empty;
        public string Region { get; set; } = string.Empty;
        public string ProcessingMode { get; set; } = string.Empty;
    }

    public class BlueprintProjectStatus
    {
        public string ProjectName { get; set; } = string.Empty;
        public string ProjectArn { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public string AdapterStatus { get; set; } = string.Empty;
        public string S3Bucket { get; set; } = string.Empty;
        public int DocumentCount { get; set; }
        public double CreatedAt { get; set; }
        public double LastUpdated { get; set; }
    }

    public class DocumentUploadResult
    {
        public string DocumentKey { get; set; } = string.Empty;
        public string S3Uri { get; set; } = string.Empty;
        public string MetadataKey { get; set; } = string.Empty;
        public long UploadTimestamp { get; set; }
        
        // BDA-specific properties
        public string? InvocationArn { get; set; }
        public string? ProjectArn { get; set; }
        public string? ProjectBucket { get; set; }
        public string? ResultsS3Uri { get; set; }
        public string Status { get; set; } = string.Empty;
        public string Service { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
        public DocumentProcessingResult? ProcessingResult { get; set; }
    }