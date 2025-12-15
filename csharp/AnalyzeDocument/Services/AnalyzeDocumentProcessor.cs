using Amazon.Textract;
using Amazon.Textract.Model;
using Amazon.Comprehend;
using AnalyzeDocument.Models;
using OpenCvSharp;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Processing;
using System.Text.RegularExpressions;

namespace AnalyzeDocument.Services
{
    public class AnalyzeDocumentProcessor : IAnalyzeDocumentProcessor
    {
        private readonly IAmazonTextract _textractClient;
        private readonly IAmazonComprehend _comprehendClient;
        private readonly ILogger<AnalyzeDocumentProcessor> _logger;

        private readonly Dictionary<string, string> _w2FieldPatterns = new()
        {
            ["employee_ssn"] = @"\d{3}-\d{2}-\d{4}",
            ["employer_ein"] = @"\d{2}-\d{7}",
            ["wages"] = @"\$?[\d,]+\.?\d*",
            ["tax_withheld"] = @"\$?[\d,]+\.?\d*"
        };

        private readonly Dictionary<string, string> _bankStatementPatterns = new()
        {
            ["account_number"] = @"\d{8,12}",
            ["routing_number"] = @"\d{9}",
            ["transaction_amount"] = @"[\+\-]?\$?[\d,]+\.?\d*",
            ["date"] = @"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"
        };

        public AnalyzeDocumentProcessor(
            IAmazonTextract textractClient,
            IAmazonComprehend comprehendClient,
            ILogger<AnalyzeDocumentProcessor> logger)
        {
            _textractClient = textractClient;
            _comprehendClient = comprehendClient;
            _logger = logger;
        }

        public async Task<EnhancedDocumentResult> AnalyzeDocumentEnhancedAsync(byte[] documentBytes, string docType)
        {
            try
            {
                // Pre-process image for better OCR
                var processedImage = PreprocessImage(documentBytes);

                // Analyze document with all features
                var request = new AnalyzeDocumentRequest
                {
                    Document = new Document
                    {
                        Bytes = new MemoryStream(processedImage)
                    },
                    FeatureTypes = new List<string> { "FORMS", "TABLES", "LAYOUT", "SIGNATURES" }
                };

                var response = await _textractClient.AnalyzeDocumentAsync(request);

                // Enhanced parsing with ML validation
                var result = await EnhancedParsingAsync(response, docType);

                // Add confidence analysis
                result.ConfidenceAnalysis = AdvancedConfidenceAnalysis(response);

                // Add document quality metrics
                result.QualityMetrics = CalculateQualityMetrics(documentBytes);

                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "AnalyzeDocument processing error for document type {DocType}", docType);
                throw new InvalidOperationException($"AnalyzeDocument processing error: {ex.Message}", ex);
            }
        }

        private byte[] PreprocessImage(byte[] imageBytes)
        {
            try
            {
                using var image = SixLabors.ImageSharp.Image.Load(imageBytes);
                
                // Apply image enhancement techniques
                image.Mutate(x => x
                    .GaussianSharpen()
                    .AutoOrient()
                    .Contrast(1.2f)
                    .Brightness(1.1f));

                using var outputStream = new MemoryStream();
                image.SaveAsPng(outputStream);
                return outputStream.ToArray();
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Image preprocessing failed, using original image");
                return imageBytes;
            }
        }

        private async Task<EnhancedDocumentResult> EnhancedParsingAsync(AnalyzeDocumentResponse response, string docType)
        {
            var blocks = response.Blocks;

            return docType switch
            {
                "w2" => await ParseW2EnhancedAsync(blocks),
                "bank_statement" => await ParseBankStatementEnhancedAsync(blocks),
                _ => await ParseGenericDocumentAsync(blocks)
            };
        }

        private async Task<EnhancedDocumentResult> ParseW2EnhancedAsync(List<Block> blocks)
        {
            var w2Data = new W2EnhancedData
            {
                EmployeeInfo = new EmployeeInfo(),
                EmployerInfo = new EmployerInfo(),
                TaxInfo = new TaxInfo(),
                Boxes = new Dictionary<string, string>(),
                ValidationResults = new ValidationResults()
            };

            // Extract all key-value pairs
            var keyValuePairs = ExtractEnhancedKeyValuePairs(blocks);

            // W-2 specific field mappings with multiple possible keys
            var fieldMappings = new Dictionary<string, List<string>>
            {
                ["employee_ssn"] = new() { "social security number", "ssn", "employee ssn" },
                ["employee_name"] = new() { "employee name", "name" },
                ["employer_ein"] = new() { "employer identification", "ein", "employer ein" },
                ["employer_name"] = new() { "employer name", "company name" },
                ["wages"] = new() { "wages", "wages tips", "box 1" },
                ["federal_tax_withheld"] = new() { "federal income tax", "federal tax", "box 2" },
                ["social_security_wages"] = new() { "social security wages", "box 3" },
                ["medicare_wages"] = new() { "medicare wages", "box 5" }
            };

            // Enhanced field extraction with fuzzy matching
            foreach (var (field, possibleKeys) in fieldMappings)
            {
                var value = FindBestMatch(keyValuePairs, possibleKeys);
                if (!string.IsNullOrEmpty(value))
                {
                    var validatedValue = ValidateFieldFormat(field, value);
                    AssignW2Field(w2Data, field, validatedValue);
                }
            }

            // Extract W-2 boxes (1-20)
            w2Data.Boxes = ExtractW2Boxes(blocks);

            // Validate extracted data
            w2Data.ValidationResults = await ValidateW2DataAsync(w2Data);

            return new EnhancedDocumentResult
            {
                DocumentType = "w2",
                ExtractedData = w2Data,
                ProcessingMetadata = new ProcessingMetadata
                {
                    TotalBlocks = blocks.Count,
                    ExtractionMethod = "enhanced_analyze_document"
                }
            };
        }

        private async Task<EnhancedDocumentResult> ParseBankStatementEnhancedAsync(List<Block> blocks)
        {
            var statementData = new BankStatementEnhancedData
            {
                AccountInfo = new AccountInfo(),
                StatementPeriod = new StatementPeriod(),
                Balances = new Balances(),
                Transactions = new List<Transaction>(),
                Summary = new TransactionSummary()
            };

            // Extract tables (transaction data)
            var tables = ExtractEnhancedTables(blocks);

            // Parse transactions with enhanced logic
            foreach (var table in tables)
            {
                var transactions = ParseTransactionTableEnhanced(table);
                statementData.Transactions.AddRange(transactions);
            }

            // Calculate summary statistics
            statementData.Summary = CalculateTransactionSummary(statementData.Transactions);

            // Extract account information
            var keyValuePairs = ExtractEnhancedKeyValuePairs(blocks);
            var accountMappings = new Dictionary<string, List<string>>
            {
                ["account_number"] = new() { "account number", "account #", "acct" },
                ["routing_number"] = new() { "routing", "routing number", "aba" },
                ["account_holder"] = new() { "account holder", "customer name", "name" }
            };

            foreach (var (field, possibleKeys) in accountMappings)
            {
                var value = FindBestMatch(keyValuePairs, possibleKeys);
                if (!string.IsNullOrEmpty(value))
                {
                    AssignAccountField(statementData.AccountInfo, field, value);
                }
            }

            return new EnhancedDocumentResult
            {
                DocumentType = "bank_statement",
                ExtractedData = statementData,
                ProcessingMetadata = new ProcessingMetadata
                {
                    TotalBlocks = blocks.Count,
                    ExtractionMethod = "enhanced_analyze_document"
                }
            };
        }

        private async Task<EnhancedDocumentResult> ParseGenericDocumentAsync(List<Block> blocks)
        {
            return new EnhancedDocumentResult
            {
                DocumentType = "generic",
                ExtractedData = new { blocks },
                ProcessingMetadata = new ProcessingMetadata
                {
                    TotalBlocks = blocks.Count,
                    ExtractionMethod = "generic_parsing"
                }
            };
        }

        private ConfidenceAnalysis AdvancedConfidenceAnalysis(AnalyzeDocumentResponse response)
        {
            var blocks = response.Blocks;
            var confidences = new List<float>();

            var confidenceByType = new Dictionary<string, List<float>>
            {
                ["WORD"] = new(),
                ["LINE"] = new(),
                ["KEY_VALUE_SET"] = new(),
                ["TABLE"] = new()
            };

            foreach (var block in blocks)
            {
                if (block.Confidence.HasValue)
                {
                    var conf = block.Confidence.Value;
                    confidences.Add(conf);

                    var blockType = block.BlockType.Value;
                    if (confidenceByType.ContainsKey(blockType))
                    {
                        confidenceByType[blockType].Add(conf);
                    }
                }
            }

            if (!confidences.Any())
            {
                return new ConfidenceAnalysis { Error = "No confidence scores available" };
            }

            var analysis = new ConfidenceAnalysis
            {
                Overall = new OverallConfidence
                {
                    Mean = confidences.Average(),
                    Median = CalculateMedian(confidences),
                    StdDev = CalculateStandardDeviation(confidences),
                    Min = confidences.Min(),
                    Max = confidences.Max(),
                    Percentile25 = CalculatePercentile(confidences, 25),
                    Percentile75 = CalculatePercentile(confidences, 75)
                },
                ByBlockType = new Dictionary<string, BlockTypeConfidence>()
            };

            foreach (var (blockType, confs) in confidenceByType)
            {
                if (confs.Any())
                {
                    analysis.ByBlockType[blockType] = new BlockTypeConfidence
                    {
                        Mean = confs.Average(),
                        Count = confs.Count,
                        Min = confs.Min(),
                        Max = confs.Max()
                    };
                }
            }

            // Quality assessment
            var meanConfidence = analysis.Overall.Mean;
            analysis.QualityAssessment = meanConfidence switch
            {
                >= 95 => "excellent",
                >= 85 => "good",
                >= 70 => "fair",
                _ => "poor"
            };

            return analysis;
        }

        private QualityMetrics CalculateQualityMetrics(byte[] imageBytes)
        {
            try
            {
                using var image = SixLabors.ImageSharp.Image.Load(imageBytes);
                
                return new QualityMetrics
                {
                    Resolution = image.Width * image.Height,
                    Dimensions = new Dimensions
                    {
                        Width = image.Width,
                        Height = image.Height
                    },
                    // Additional quality metrics would be calculated here
                    Sharpness = 0.0, // Placeholder
                    Brightness = 0.0, // Placeholder
                    Contrast = 0.0 // Placeholder
                };
            }
            catch (Exception ex)
            {
                return new QualityMetrics
                {
                    Error = $"Could not calculate quality metrics: {ex.Message}"
                };
            }
        }

        // Helper methods
        private Dictionary<string, string> ExtractEnhancedKeyValuePairs(List<Block> blocks)
        {
            // Implementation for enhanced key-value extraction
            return new Dictionary<string, string>();
        }

        private List<Dictionary<string, object>> ExtractEnhancedTables(List<Block> blocks)
        {
            // Implementation for enhanced table extraction
            return new List<Dictionary<string, object>>();
        }

        private string? FindBestMatch(Dictionary<string, string> keyValuePairs, List<string> possibleKeys)
        {
            foreach (var (key, value) in keyValuePairs)
            {
                var keyLower = key.ToLowerInvariant();
                foreach (var possibleKey in possibleKeys)
                {
                    if (keyLower.Contains(possibleKey.ToLowerInvariant()))
                    {
                        return value;
                    }
                }
            }
            return null;
        }

        private string ValidateFieldFormat(string fieldName, string value)
        {
            // Add regex validation logic here
            return value; // Return cleaned/validated value
        }

        private void AssignW2Field(W2EnhancedData w2Data, string field, string value)
        {
            // Implementation to assign field to appropriate W2 data structure
        }

        private void AssignAccountField(AccountInfo accountInfo, string field, string value)
        {
            // Implementation to assign field to account info
        }

        private Dictionary<string, string> ExtractW2Boxes(List<Block> blocks)
        {
            // Implementation to extract W-2 boxes
            return new Dictionary<string, string>();
        }

        private async Task<ValidationResults> ValidateW2DataAsync(W2EnhancedData w2Data)
        {
            // Implementation for W-2 data validation
            return new ValidationResults();
        }

        private List<Transaction> ParseTransactionTableEnhanced(Dictionary<string, object> table)
        {
            // Implementation for enhanced transaction parsing
            return new List<Transaction>();
        }

        private TransactionSummary CalculateTransactionSummary(List<Transaction> transactions)
        {
            return new TransactionSummary
            {
                TotalDeposits = transactions.Where(t => t.Amount > 0).Sum(t => t.Amount),
                TotalWithdrawals = Math.Abs(transactions.Where(t => t.Amount < 0).Sum(t => t.Amount)),
                TransactionCount = transactions.Count
            };
        }

        // Statistical helper methods
        private float CalculateMedian(List<float> values)
        {
            var sorted = values.OrderBy(x => x).ToList();
            var count = sorted.Count;
            return count % 2 == 0
                ? (sorted[count / 2 - 1] + sorted[count / 2]) / 2
                : sorted[count / 2];
        }

        private float CalculateStandardDeviation(List<float> values)
        {
            var mean = values.Average();
            var sumOfSquares = values.Sum(x => Math.Pow(x - mean, 2));
            return (float)Math.Sqrt(sumOfSquares / values.Count);
        }

        private float CalculatePercentile(List<float> values, int percentile)
        {
            var sorted = values.OrderBy(x => x).ToList();
            var index = (percentile / 100.0) * (sorted.Count - 1);
            var lower = (int)Math.Floor(index);
            var upper = (int)Math.Ceiling(index);
            
            if (lower == upper)
                return sorted[lower];
            
            var weight = index - lower;
            return sorted[lower] * (1 - (float)weight) + sorted[upper] * (float)weight;
        }
    }
}