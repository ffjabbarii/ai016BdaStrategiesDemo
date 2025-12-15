using Amazon.Textract;
using Amazon.Comprehend;
using AnalyzeDocument.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add AWS services
builder.Services.AddAWSService<IAmazonTextract>();
builder.Services.AddAWSService<IAmazonComprehend>();
builder.Services.AddScoped<IAnalyzeDocumentProcessor, AnalyzeDocumentProcessor>();

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