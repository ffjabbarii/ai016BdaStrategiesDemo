using Amazon.Textract;
using Amazon.Textract.Model;
using Amazon.S3;
using Textract.Models;

namespace Textract.Services
{
    public class TextractProcessor : ITextractProcessor
    {
        private readonly IAmazonTextract _textractClient;
        private readonly IAmazonS3 _s3Client;

        public TextractProcessor(IAmazonTextract textractClient, IAmazonS3 s3Client)
        {
            _textractClient = textractClient;
            _s3Client = s3Client;
        }

        public async Task<DocumentProcessingResult> ProcessDocumentSyncAsync(byte[] documentBytes, string docType)
        {
            try
            {
                // Detect text
                var textRequest = new DetectDocumentTextRequest
                {
                    Document = new Document
                    {
                        Bytes = new MemoryStream(documentBytes)
                    }
                };

                var textResponse = await _textractClient.DetectDocumentTextAsync(textRequest);

                // Analyze forms and tables
                var analyzeRequest = new AnalyzeDocumentRequest
                {
                    Document = new Document
                    {
                        Bytes = new MemoryStream(documentBytes)
                    },
                    FeatureTypes = new List<string> { "FORMS", "TABLES" }
                };

                var analyzeResponse = await _textractClient.AnalyzeDocumentAsync(analyzeRequest);

                return ParseTextractResponse(textResponse, analyzeResponse, docType);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Textract processing error: {ex.Message}", ex);
            }
        }

        public async Task<string> ProcessDocumentAsync(string s3Bucket, string s3Key, string docType)
        {
            try
            {
                var request = new StartDocumentAnalysisRequest
                {
                    DocumentLocation = new DocumentLocation
                    {
                        S3Object = new S3Object
                        {
                            Bucket = s3Bucket,
                            Name = s3Key
                        }
                    },
                    FeatureTypes = new List<string> { "FORMS", "TABLES" }
                };

                var response = await _textractClient.StartDocumentAnalysisAsync(request);
                return response.JobId;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Textract async processing error: {ex.Message}", ex);
            }
        }

        public async Task<DocumentProcessingResult> GetAsyncResultsAsync(string jobId, string docType)
        {
            try
            {
                var request = new GetDocumentAnalysisRequest
                {
                    JobId = jobId
                };

                var response = await _textractClient.GetDocumentAnalysisAsync(request);

                return response.JobStatus switch
                {
                    JobStatus.SUCCEEDED => ParseTextractResponse(null, response, docType),
                    JobStatus.FAILED => throw new InvalidOperationException($"Textract job failed: {response.StatusMessage}"),
                    _ => new DocumentProcessingResult
                    {
                        Status = response.JobStatus.Value,
                        JobId = jobId
                    }
                };
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Error getting async results: {ex.Message}", ex);
            }
        }

        private DocumentProcessingResult ParseTextractResponse(
            DetectDocumentTextResponse? textResponse,
            AnalyzeDocumentResponse analyzeResponse,
            string docType)
        {
            return docType switch
            {
                "w2" => ParseW2Document(textResponse, analyzeResponse),
                "bank_statement" => ParseBankStatement(textResponse, analyzeResponse),
                _ => new DocumentProcessingResult { RawResponse = analyzeResponse }
            };
        }

        private DocumentProcessingResult ParseW2Document(
            DetectDocumentTextResponse? textResponse,
            AnalyzeDocumentResponse analyzeResponse)
        {
            var w2Fields = new Dictionary<string, string?>
            {
                ["employee_ssn"] = null,
                ["employee_name"] = null,
                ["employer_ein"] = null,
                ["employer_name"] = null,
                ["wages"] = null,
                ["federal_tax_withheld"] = null,
                ["social_security_wages"] = null,
                ["medicare_wages"] = null
            };

            var blocks = analyzeResponse.Blocks;
            var keyValuePairs = ExtractKeyValuePairs(blocks);

            // Map Textract fields to W-2 fields
            var fieldMappings = new Dictionary<string, string>
            {
                ["Employee's social security number"] = "employee_ssn",
                ["Employee's name"] = "employee_name",
                ["Employer identification number"] = "employer_ein",
                ["Employer's name"] = "employer_name",
                ["Wages, tips, other compensation"] = "wages",
                ["Federal income tax withheld"] = "federal_tax_withheld"
            };

            foreach (var (key, value) in keyValuePairs)
            {
                foreach (var (mappingKey, fieldName) in fieldMappings)
                {
                    if (key.Contains(mappingKey, StringComparison.OrdinalIgnoreCase))
                    {
                        w2Fields[fieldName] = value;
                        break;
                    }
                }
            }

            return new DocumentProcessingResult
            {
                DocumentType = "w2",
                ExtractedFields = w2Fields,
                ConfidenceScores = CalculateConfidenceScores(blocks),
                RawKeyValuePairs = keyValuePairs
            };
        }

        private DocumentProcessingResult ParseBankStatement(
            DetectDocumentTextResponse? textResponse,
            AnalyzeDocumentResponse analyzeResponse)
        {
            var statementData = new Dictionary<string, object?>
            {
                ["account_number"] = null,
                ["account_holder"] = null,
                ["statement_period"] = null,
                ["beginning_balance"] = null,
                ["ending_balance"] = null,
                ["transactions"] = new List<Dictionary<string, object>>()
            };

            var blocks = analyzeResponse.Blocks;

            // Extract tables (transactions)
            var tables = ExtractTables(blocks);
            statementData["transactions"] = ParseTransactionTables(tables);

            // Extract key information
            var keyValuePairs = ExtractKeyValuePairs(blocks);

            return new DocumentProcessingResult
            {
                DocumentType = "bank_statement",
                ExtractedFields = statementData,
                ConfidenceScores = CalculateConfidenceScores(blocks),
                RawKeyValuePairs = keyValuePairs
            };
        }

        private Dictionary<string, string> ExtractKeyValuePairs(List<Block> blocks)
        {
            var keyValuePairs = new Dictionary<string, string>();

            foreach (var block in blocks.Where(b => b.BlockType == BlockType.KEY_VALUE_SET))
            {
                if (block.EntityTypes?.Contains("KEY") == true)
                {
                    var keyText = GetTextFromRelationships(block, blocks);
                    var valueText = GetValueFromKeyBlock(block, blocks);
                    
                    if (!string.IsNullOrEmpty(keyText) && !string.IsNullOrEmpty(valueText))
                    {
                        keyValuePairs[keyText] = valueText;
                    }
                }
            }

            return keyValuePairs;
        }

        private List<Dictionary<string, object>> ExtractTables(List<Block> blocks)
        {
            var tables = new List<Dictionary<string, object>>();

            foreach (var block in blocks.Where(b => b.BlockType == BlockType.TABLE))
            {
                var tableData = ParseTableBlock(block, blocks);
                tables.Add(tableData);
            }

            return tables;
        }

        private string GetTextFromRelationships(Block block, List<Block> allBlocks)
        {
            var textParts = new List<string>();

            if (block.Relationships != null)
            {
                foreach (var relationship in block.Relationships.Where(r => r.Type == RelationshipType.CHILD))
                {
                    foreach (var childId in relationship.Ids)
                    {
                        var childBlock = allBlocks.FirstOrDefault(b => b.Id == childId);
                        if (childBlock?.BlockType == BlockType.WORD)
                        {
                            textParts.Add(childBlock.Text ?? "");
                        }
                    }
                }
            }

            return string.Join(" ", textParts);
        }

        private string GetValueFromKeyBlock(Block keyBlock, List<Block> allBlocks)
        {
            // Implementation to get value from key block relationships
            // This would involve traversing the relationships to find the associated value
            return "";
        }

        private Dictionary<string, object> ParseTableBlock(Block tableBlock, List<Block> allBlocks)
        {
            // Implementation to parse table structure
            return new Dictionary<string, object>();
        }

        private List<Dictionary<string, object>> ParseTransactionTables(List<Dictionary<string, object>> tables)
        {
            // Implementation to parse transaction data from tables
            return new List<Dictionary<string, object>>();
        }

        private Dictionary<string, double> CalculateConfidenceScores(List<Block> blocks)
        {
            var confidences = blocks
                .Where(b => b.Confidence.HasValue)
                .Select(b => b.Confidence.Value)
                .ToList();

            if (!confidences.Any())
            {
                return new Dictionary<string, double>
                {
                    ["average"] = 0.0,
                    ["minimum"] = 0.0,
                    ["maximum"] = 0.0
                };
            }

            return new Dictionary<string, double>
            {
                ["average"] = confidences.Average(),
                ["minimum"] = confidences.Min(),
                ["maximum"] = confidences.Max()
            };
        }
    }
}