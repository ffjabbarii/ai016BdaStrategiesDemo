using Textract.Models;

namespace Textract.Services
{
    public interface ITextractProcessor
    {
        Task<DocumentProcessingResult> ProcessDocumentSyncAsync(byte[] documentBytes, string docType);
        Task<string> ProcessDocumentAsync(string s3Bucket, string s3Key, string docType);
        Task<DocumentProcessingResult> GetAsyncResultsAsync(string jobId, string docType);
    }
}