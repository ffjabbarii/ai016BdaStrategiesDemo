using Microsoft.AspNetCore.Mvc;
using BlueprintAPI.Services;
using BlueprintAPI.Models;

namespace BlueprintAPI.Controllers
{
    [ApiController]
    [Route("")]
    public class DocumentController : ControllerBase
    {
        private readonly IBlueprintProcessor _blueprintProcessor;
        private readonly ILogger<DocumentController> _logger;

        public DocumentController(IBlueprintProcessor blueprintProcessor, ILogger<DocumentController> logger)
        {
            _blueprintProcessor = blueprintProcessor;
            _logger = logger;
        }

        [HttpGet("")]
        public IActionResult Root()
        {
            return Ok(new
            {
                Message = "🔥 C# Blueprint API v3.0 - UPDATED CODE RUNNING - Dec 14, 2025 🔥",
                Status = "running",
                Version = "3.0.0",
                Debug = "This is the LATEST C# code with debugging!",
                Language = "C#"
            });
        }

        [HttpGet("health")]
        public IActionResult HealthCheck()
        {
            return Ok(new
            {
                Status = "healthy",
                Version = "3.0.0",
                Timestamp = "2025-12-14",
                Message = "🚀 Latest C# Blueprint API code is running!",
                Language = "C#"
            });
        }

        [HttpPost("process/w2")]
        public async Task<IActionResult> ProcessW2([FromForm] IFormFile file)
        {
            try
            {
                _logger.LogInformation("🔥🔥🔥 C# API PROCESSING W-2 - UPDATED CODE v3.0 🔥🔥🔥");
                _logger.LogInformation($"📄 Processing file: {file?.FileName}");
                _logger.LogInformation($"📊 File size: {file?.Length} bytes");

                if (file == null || file.Length == 0)
                {
                    return BadRequest(new { Detail = "Empty file uploaded" });
                }

                // File validation
                var allowedTypes = new[] { "image/jpeg", "image/png", "application/pdf" };
                if (!allowedTypes.Contains(file.ContentType))
                {
                    return BadRequest(new { Detail = $"Unsupported file type: {file.ContentType}. Supported: JPEG, PNG, PDF" });
                }

                using var memoryStream = new MemoryStream();
                await file.CopyToAsync(memoryStream);
                var fileBytes = memoryStream.ToArray();

                _logger.LogInformation("🚀 Sending to C# BlueprintProcessor...");
                var result = await _blueprintProcessor.ProcessDocumentAsync(fileBytes, "w2");

                return Ok(new
                {
                    Status = "success",
                    DocumentType = "w2",
                    BlueprintResult = result,
                    Filename = file.FileName,
                    Message = "Document processed using real AWS Blueprint API (C#)",
                    Language = "C#"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ C# Blueprint processing failed");
                return StatusCode(500, new { Detail = $"Blueprint processing failed: {ex.Message}" });
            }
        }

        [HttpPost("process/bank-statement")]
        public async Task<IActionResult> ProcessBankStatement([FromForm] IFormFile file)
        {
            try
            {
                _logger.LogInformation("🔥🔥🔥 C# API PROCESSING BANK STATEMENT - UPDATED CODE v3.0 🔥🔥🔥");

                if (file == null || file.Length == 0)
                {
                    return BadRequest(new { Detail = "Empty file uploaded" });
                }

                var allowedExtensions = new[] { ".pdf", ".png", ".jpg", ".jpeg" };
                var fileExtension = Path.GetExtension(file.FileName).ToLower();
                if (!allowedExtensions.Contains(fileExtension))
                {
                    return BadRequest(new { Detail = "Only PDF and image files are supported" });
                }

                using var memoryStream = new MemoryStream();
                await file.CopyToAsync(memoryStream);
                var fileBytes = memoryStream.ToArray();

                var result = await _blueprintProcessor.ProcessDocumentAsync(fileBytes, "bank_statement");

                return Ok(new
                {
                    Status = "success",
                    DocumentType = "bank_statement",
                    BlueprintResult = result,
                    Filename = file.FileName,
                    Message = "Document processed using real AWS Blueprint API (C#)",
                    Language = "C#"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ C# Bank statement processing failed");
                return StatusCode(500, new { Detail = $"Blueprint processing failed: {ex.Message}" });
            }
        }

        // Blueprint Management Endpoints (matching Python API)
        [HttpPost("blueprint/create")]
        public async Task<IActionResult> CreateBlueprintProject([FromQuery] string projectName, [FromQuery] string documentType = "w2", [FromQuery] string description = "C# BDA Blueprint project")
        {
            try
            {
                _logger.LogInformation($"🏗️ Creating C# Blueprint project: {projectName}");
                
                var result = await _blueprintProcessor.CreateBlueprintProjectAsync(projectName, documentType, description);
                
                return Ok(new
                {
                    Status = "success",
                    ProjectArn = result.ProjectArn,
                    S3Bucket = result.S3Bucket,
                    AdapterId = result.AdapterId,
                    ProjectName = projectName,
                    DocumentType = documentType,
                    Message = $"C# Blueprint project '{projectName}' created in your AWS account with S3 bucket and Textract Adapter",
                    Language = "C#"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ C# Blueprint project creation failed");
                return StatusCode(500, new { Detail = ex.Message });
            }
        }

        [HttpGet("blueprint/projects")]
        public async Task<IActionResult> ListBlueprintProjects()
        {
            try
            {
                _logger.LogInformation("📋 Listing C# Blueprint projects...");
                
                var projects = await _blueprintProcessor.ListBlueprintProjectsAsync();
                
                return Ok(new
                {
                    Status = "success",
                    Projects = projects,
                    Count = projects.Count,
                    Message = $"Found {projects.Count} C# Blueprint projects in your AWS account",
                    Language = "C#"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Failed to list C# Blueprint projects");
                return StatusCode(500, new { Detail = ex.Message });
            }
        }

        [HttpGet("blueprint/project/{projectArn}/status")]
        public async Task<IActionResult> GetProjectStatus(string projectArn)
        {
            try
            {
                _logger.LogInformation($"🔍 Getting C# project status: {projectArn}");
                
                var status = await _blueprintProcessor.GetProjectStatusAsync(projectArn);
                
                return Ok(new
                {
                    Status = "success",
                    ProjectStatus = status,
                    Language = "C#"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Failed to get C# project status");
                return StatusCode(500, new { Detail = ex.Message });
            }
        }

        [HttpPost("blueprint/project/{projectName}/upload")]
        public async Task<IActionResult> UploadDocumentToProject(string projectName, [FromForm] IFormFile file)
        {
            try
            {
                _logger.LogInformation($"📤 Uploading document to C# Blueprint project: {projectName}");

                if (file == null || file.Length == 0)
                {
                    return BadRequest(new { Detail = "Empty file uploaded" });
                }

                using var memoryStream = new MemoryStream();
                await file.CopyToAsync(memoryStream);
                var fileBytes = memoryStream.ToArray();

                var result = await _blueprintProcessor.UploadDocumentToProjectAsync(projectName, fileBytes, file.FileName);

                return Ok(new
                {
                    Status = "success",
                    ProjectName = projectName,
                    Filename = file.FileName,
                    S3Uri = result.S3Uri,
                    DocumentKey = result.DocumentKey,
                    UploadTimestamp = result.UploadTimestamp,
                    Message = $"Document uploaded to C# Blueprint project '{projectName}' in your AWS account",
                    Language = "C#"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ C# Document upload failed");
                return StatusCode(500, new { Detail = ex.Message });
            }
        }
    }
}