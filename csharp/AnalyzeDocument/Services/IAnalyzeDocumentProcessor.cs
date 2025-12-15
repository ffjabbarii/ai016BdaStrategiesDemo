using AnalyzeDocument.Models;

namespace AnalyzeDocument.Services
{
    public interface IAnalyzeDocumentProcessor
    {
        Task<EnhancedDocumentResult> AnalyzeDocumentEnhancedAsync(byte[] documentBytes, string docType);
    }
}