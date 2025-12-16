using BlueprintAPI.Models;

namespace BlueprintAPI.Services
{
    public interface IBlueprintProcessor
    {
        Task<DocumentProcessingResult> ProcessDocumentAsync(byte[] documentBytes, string docType);
        Task<BlueprintProjectResult> CreateBlueprintProjectAsync(string projectName, string documentType, string description);
        Task<List<BlueprintProject>> ListBlueprintProjectsAsync();
        Task<BlueprintProjectStatus> GetProjectStatusAsync(string projectArn);
        Task<DocumentUploadResult> UploadDocumentToProjectAsync(string projectName, byte[] documentBytes, string filename);
        Task<string> CreateAdapterAsync(string adapterName, string documentType, List<string> featureTypes);
    }
}