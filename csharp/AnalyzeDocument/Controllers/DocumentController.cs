using Microsoft.AspNetCore.Mvc;
using AnalyzeDocument.Services;

namespace AnalyzeDocument.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DocumentController : ControllerBase
    {
        private readonly IAnalyzeDocumentProcessor _processor;
        private readonly ILogger<DocumentController> _logger;

        public DocumentController(IAnalyzeDocumentProcessor processor, ILogger<DocumentController> logger)
        {
            _processor = processor;
            _logger = logger;
        }

        [HttpPost("analyze/w2")]
        public async Task<IActionResult> AnalyzeW2([FromForm] IFormFile file)
        {
            try
            {
                if (file == null || file.Length == 0)
                {
                    return BadRequest("No file uploaded");
                }

                using var memoryStream = new MemoryStream();
                await file.CopyToAsync(memoryStream);
                var fileBytes = memoryStream.ToArray();

                var result = await _processor.AnalyzeDocumentEnhancedAsync(fileBytes, "w2");

                return Ok(new
                {
                    Status = "success",
                    DocumentType = "w2",
                    Result = result,
                    Filename = file.FileName
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error analyzing W-2 document");
                return StatusCode(500, new { Error = ex.Message });
            }
        }

        [HttpPost("analyze/bank-statement")]
        public async Task<IActionResult> AnalyzeBankStatement([FromForm] IFormFile file)
        {
            try
            {
                if (file == null || file.Length == 0)
                {
                    return BadRequest("No file uploaded");
                }

                using var memoryStream = new MemoryStream();
                await file.CopyToAsync(memoryStream);
                var fileBytes = memoryStream.ToArray();

                var result = await _processor.AnalyzeDocumentEnhancedAsync(fileBytes, "bank_statement");

                return Ok(new
                {
                    Status = "success",
                    DocumentType = "bank_statement",
                    Result = result,
                    Filename = file.FileName
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error analyzing bank statement");
                return StatusCode(500, new { Error = ex.Message });
            }
        }

        [HttpGet("health")]
        public IActionResult HealthCheck()
        {
            return Ok(new { Status = "healthy", Service = "analyze-document-csharp" });
        }
    }
}