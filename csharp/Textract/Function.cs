using Amazon.Lambda.Core;
using Amazon.Lambda.S3Events;
using Amazon.S3;
using Amazon.Textract;
using Textract.Services;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace Textract;

public class Function
{
    private readonly IAmazonS3 _s3Client;
    private readonly ITextractProcessor _textractProcessor;

    public Function()
    {
        _s3Client = new AmazonS3Client();
        _textractProcessor = new TextractProcessor(new AmazonTextractClient(), _s3Client);
    }

    /// <summary>
    /// Lambda function handler for S3 events
    /// </summary>
    public async Task<string> FunctionHandler(S3Event evnt, ILambdaContext context)
    {
        var results = new List<string>();

        foreach (var record in evnt.Records)
        {
            try
            {
                var bucketName = record.S3.Bucket.Name;
                var objectKey = record.S3.Object.Key;
                
                context.Logger.LogInformation($"Processing document: {objectKey} from bucket: {bucketName}");

                // Determine document type from file name or metadata
                var docType = DetermineDocumentType(objectKey);
                
                // Start async processing
                var jobId = await _textractProcessor.ProcessDocumentAsync(bucketName, objectKey, docType);
                
                context.Logger.LogInformation($"Started Textract job: {jobId} for document: {objectKey}");
                results.Add($"Job {jobId} started for {objectKey}");
            }
            catch (Exception ex)
            {
                context.Logger.LogError($"Error processing {record.S3.Object.Key}: {ex.Message}");
                results.Add($"Error processing {record.S3.Object.Key}: {ex.Message}");
            }
        }

        return string.Join("; ", results);
    }

    private static string DetermineDocumentType(string objectKey)
    {
        var fileName = Path.GetFileName(objectKey).ToLowerInvariant();
        
        if (fileName.Contains("w2") || fileName.Contains("w-2"))
            return "w2";
        
        if (fileName.Contains("bank") || fileName.Contains("statement"))
            return "bank_statement";
        
        return "unknown";
    }
}