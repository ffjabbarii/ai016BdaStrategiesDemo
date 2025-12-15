using Amazon.Textract.Model;

namespace Textract.Models
{
    public class DocumentProcessingResult
    {
        public string DocumentType { get; set; } = string.Empty;
        public object? ExtractedFields { get; set; }
        public Dictionary<string, double>? ConfidenceScores { get; set; }
        public Dictionary<string, string>? RawKeyValuePairs { get; set; }
        public object? RawResponse { get; set; }
        public string Status { get; set; } = string.Empty;
        public string JobId { get; set; } = string.Empty;
    }
}