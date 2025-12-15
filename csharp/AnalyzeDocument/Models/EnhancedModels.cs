namespace AnalyzeDocument.Models
{
    public class EnhancedDocumentResult
    {
        public string DocumentType { get; set; } = string.Empty;
        public object? ExtractedData { get; set; }
        public ProcessingMetadata? ProcessingMetadata { get; set; }
        public ConfidenceAnalysis? ConfidenceAnalysis { get; set; }
        public QualityMetrics? QualityMetrics { get; set; }
    }

    public class ProcessingMetadata
    {
        public int TotalBlocks { get; set; }
        public string ExtractionMethod { get; set; } = string.Empty;
    }

    public class W2EnhancedData
    {
        public EmployeeInfo EmployeeInfo { get; set; } = new();
        public EmployerInfo EmployerInfo { get; set; } = new();
        public TaxInfo TaxInfo { get; set; } = new();
        public Dictionary<string, string> Boxes { get; set; } = new();
        public ValidationResults ValidationResults { get; set; } = new();
    }

    public class BankStatementEnhancedData
    {
        public AccountInfo AccountInfo { get; set; } = new();
        public StatementPeriod StatementPeriod { get; set; } = new();
        public Balances Balances { get; set; } = new();
        public List<Transaction> Transactions { get; set; } = new();
        public TransactionSummary Summary { get; set; } = new();
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

    public class AccountInfo
    {
        public string? AccountNumber { get; set; }
        public string? RoutingNumber { get; set; }
        public string? AccountHolder { get; set; }
        public string? BankName { get; set; }
    }

    public class StatementPeriod
    {
        public DateTime? StartDate { get; set; }
        public DateTime? EndDate { get; set; }
    }

    public class Balances
    {
        public decimal? BeginningBalance { get; set; }
        public decimal? EndingBalance { get; set; }
        public decimal? AverageBalance { get; set; }
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

    public class ValidationResults
    {
        public bool IsValid { get; set; }
        public List<string> Errors { get; set; } = new();
        public List<string> Warnings { get; set; } = new();
    }

    public class ConfidenceAnalysis
    {
        public OverallConfidence Overall { get; set; } = new();
        public Dictionary<string, BlockTypeConfidence> ByBlockType { get; set; } = new();
        public string QualityAssessment { get; set; } = string.Empty;
        public string? Error { get; set; }
    }

    public class OverallConfidence
    {
        public float Mean { get; set; }
        public float Median { get; set; }
        public float StdDev { get; set; }
        public float Min { get; set; }
        public float Max { get; set; }
        public float Percentile25 { get; set; }
        public float Percentile75 { get; set; }
    }

    public class BlockTypeConfidence
    {
        public float Mean { get; set; }
        public int Count { get; set; }
        public float Min { get; set; }
        public float Max { get; set; }
    }

    public class QualityMetrics
    {
        public double Sharpness { get; set; }
        public double Brightness { get; set; }
        public double Contrast { get; set; }
        public int Resolution { get; set; }
        public Dimensions Dimensions { get; set; } = new();
        public string? Error { get; set; }
    }

    public class Dimensions
    {
        public int Width { get; set; }
        public int Height { get; set; }
    }
}