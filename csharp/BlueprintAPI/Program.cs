using Amazon.Textract;
using Amazon.Bedrock;
using Amazon.BedrockDataAutomation;
using Amazon.BedrockDataAutomationRuntime;
using Amazon.S3;
using BlueprintAPI.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add AWS services for BDA
builder.Services.AddAWSService<IAmazonTextract>();
builder.Services.AddAWSService<IAmazonBedrock>();
builder.Services.AddAWSService<IAmazonBedrockDataAutomation>();
builder.Services.AddAWSService<IAmazonBedrockDataAutomationRuntime>();
builder.Services.AddAWSService<IAmazonS3>();
builder.Services.AddScoped<IBlueprintProcessor, BlueprintProcessor>();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();