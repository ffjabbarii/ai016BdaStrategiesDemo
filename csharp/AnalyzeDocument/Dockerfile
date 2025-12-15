FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY ["AnalyzeDocument.csproj", "."]
RUN dotnet restore "./AnalyzeDocument.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "AnalyzeDocument.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AnalyzeDocument.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AnalyzeDocument.dll"]