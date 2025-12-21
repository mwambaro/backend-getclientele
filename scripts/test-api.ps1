# PowerShell helper: scripts/test-api.ps1
# Usage: .\test-api.ps1 -BaseUrl http://localhost:8000 -Username admin -Password password
param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$Username = "admin",
  [string]$Password = "password"
)

# Get token
Write-Host "Logging in..."
$body = @{ username = $Username; password = $Password } | ConvertTo-Json
$resp = Invoke-RestMethod -Method Post -Uri "$BaseUrl/auth/login/" -ContentType "application/json" -Body $body
$token = $resp.access
if (-not $token) { Write-Error "Failed to get access token"; exit 1 }
Write-Host "Access token obtained (truncated):" $token.Substring(0,20) "..."

$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

Write-Host "Listing vendors..."
Invoke-RestMethod -Method Get -Uri "$BaseUrl/vendors/" -Headers $headers | ConvertTo-Json -Depth 5

Write-Host "Calling AI Similar (sample)..."
$sample = @{ products = @(@{ id=1; name='Chai'; description='tea' }); product_id = 1; top_k = 3 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/ai/similar/" -Headers $headers -Body $sample -ContentType "application/json" | ConvertTo-Json -Depth 5
