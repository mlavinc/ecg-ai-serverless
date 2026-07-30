<#
.SYNOPSIS
  One-command portfolio deploy: build artifacts, terraform apply, sync frontend,
  invalidate CloudFront, health-check the API, print URLs.

.DESCRIPTION
  Idempotent: safe to re-run after a partial failure. Infrastructure names come
  from Terraform variables / outputs.
#>
$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Infra = Join-Path $Root "infra"
$Frontend = Join-Path $Root "frontend"
$ModelLocal = Join-Path $Root "data\models\random_forest_final.joblib"
$LambdaZip = Join-Path $Root "lambda.zip"

function Write-Step([string]$Message) {
  Write-Host ""
  Write-Host "==> $Message" -ForegroundColor Cyan
}

function Get-TfVarOrDefault([string]$Name, [string]$Default) {
  $envName = "TF_VAR_$Name"
  $fromEnv = [Environment]::GetEnvironmentVariable($envName)
  if ($fromEnv) { return $fromEnv }

  $tfvars = Join-Path $Infra "terraform.tfvars"
  if (Test-Path $tfvars) {
    $pattern = '^\s*' + [regex]::Escape($Name) + '\s*='
    $line = Get-Content $tfvars | Where-Object { $_ -match $pattern } | Select-Object -First 1
    if ($line -match '=\s*"([^"]+)"') { return $Matches[1] }
    if ($line -match "=\s*'([^']+)'") { return $Matches[1] }
  }
  return $Default
}

function Invoke-Tf([string[]]$TfArgs) {
  Push-Location $Infra
  try {
    & terraform @TfArgs
    if ($LASTEXITCODE -ne 0) { throw "terraform $($TfArgs -join ' ') failed (exit $LASTEXITCODE)" }
  }
  finally {
    Pop-Location
  }
}

function Get-TfOutput([string]$Name) {
  Push-Location $Infra
  try {
    $value = & terraform output -raw $Name 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($value)) {
      throw "Missing Terraform output '$Name'. Did terraform apply succeed?"
    }
    return $value.Trim()
  }
  finally {
    Pop-Location
  }
}

# --- Prerequisites ---
foreach ($cmd in @("terraform", "aws", "npm", "python")) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Required command not found on PATH: $cmd"
  }
}
if (-not (Test-Path $ModelLocal)) {
  throw "Model file not found: $ModelLocal"
}

$AwsRegion = if ($env:AWS_REGION) { $env:AWS_REGION } else { Get-TfVarOrDefault "aws_region" "sa-east-1" }
$ModelBucket = if ($env:MODEL_BUCKET) { $env:MODEL_BUCKET } else { Get-TfVarOrDefault "model_bucket_name" "ecg-ai-models-mlavinc" }
$ModelKey = if ($env:MODEL_KEY) { $env:MODEL_KEY } else { Get-TfVarOrDefault "model_key" "random_forest_final.joblib" }

Write-Host "ECG AI - portfolio deploy"
Write-Host "  region : $AwsRegion"
Write-Host ("  model  : s3://{0}/{1}" -f $ModelBucket, $ModelKey)

# --- 1. Build Lambda ZIP ---
Write-Step "Building Lambda package (scripts/build_package.py)"
Push-Location $Root
try {
  & python scripts/build_package.py
  if ($LASTEXITCODE -ne 0) { throw "build_package.py failed" }
}
finally {
  Pop-Location
}
if (-not (Test-Path $LambdaZip)) {
  throw "Expected artifact missing: $LambdaZip"
}

# --- 2. Ensure external model bucket + object exist ---
Write-Step "Ensuring trained model is in S3"
$null = & aws s3api head-bucket --bucket $ModelBucket --region $AwsRegion 2>$null
if ($LASTEXITCODE -ne 0) {
  throw ("Model bucket s3://{0} does not exist or is not accessible. Create it once outside Terraform, then re-run." -f $ModelBucket)
}

$null = & aws s3api head-object --bucket $ModelBucket --key $ModelKey --region $AwsRegion 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "  Uploading $ModelLocal ..."
  & aws s3 cp $ModelLocal ("s3://{0}/{1}" -f $ModelBucket, $ModelKey) --region $AwsRegion
  if ($LASTEXITCODE -ne 0) {
    throw ("Failed to upload model to s3://{0}/{1}" -f $ModelBucket, $ModelKey)
  }
}
else {
  Write-Host "  Model already present (skipping upload)."
}

# --- 3. Terraform (idempotent) ---
Write-Step "terraform init"
Invoke-Tf @("init", "-input=false", "-reconfigure")

Write-Step "terraform apply"
Invoke-Tf @("apply", "-auto-approve", "-input=false", "-refresh=true")

$CfUrl = Get-TfOutput "cloudfront_domain_name"
$DistId = Get-TfOutput "cloudfront_distribution_id"
$FrontendBucket = Get-TfOutput "frontend_bucket_name"
$HealthUrl = "{0}/api/health" -f $CfUrl

Write-Step ("Waiting for CloudFront distribution {0} to deploy" -f $DistId)
& aws cloudfront wait distribution-deployed --id $DistId
if ($LASTEXITCODE -ne 0) {
  Write-Host "  Warning: wait timed out or failed; continuing with sync/health checks."
}

# --- 4. Frontend build + sync ---
Write-Step "Building frontend (npm run build)"
Push-Location $Frontend
try {
  if (-not (Test-Path "node_modules")) {
    & npm install
    if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
  }
  & npm run build
  if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }
}
finally {
  Pop-Location
}

$Dist = Join-Path $Frontend "dist"
if (-not (Test-Path $Dist)) { throw "Frontend dist/ not found after build" }

Write-Step ("Syncing frontend to s3://{0}" -f $FrontendBucket)
& aws s3 sync $Dist ("s3://{0}/" -f $FrontendBucket) --delete --region $AwsRegion
if ($LASTEXITCODE -ne 0) { throw "aws s3 sync failed" }

Write-Step "Invalidating CloudFront cache"
& aws cloudfront create-invalidation --distribution-id $DistId --paths "/*" --region $AwsRegion | Out-Null
if ($LASTEXITCODE -ne 0) { throw "CloudFront invalidation failed" }

# --- 5. Health check (cold start + CDN) ---
Write-Step "Post-deploy health check: $HealthUrl"
$ok = $false
$maxAttempts = 18
for ($i = 1; $i -le $maxAttempts; $i++) {
  try {
    $resp = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 45
    if ($resp.StatusCode -eq 200 -and $resp.Content -match '"status"\s*:\s*"ok"') {
      Write-Host ("  Attempt {0}/{1}: OK ({2})" -f $i, $maxAttempts, $resp.Content)
      $ok = $true
      break
    }
    Write-Host ("  Attempt {0}/{1}: unexpected body: {2}" -f $i, $maxAttempts, $resp.Content)
  }
  catch {
    Write-Host ("  Attempt {0}/{1}: {2}" -f $i, $maxAttempts, $_.Exception.Message)
  }
  Start-Sleep -Seconds 10
}

if (-not $ok) {
  throw ("Health check failed after {0} attempts. Try manually: {1}" -f $maxAttempts, $HealthUrl)
}

Write-Host ""
Write-Host "Deploy succeeded." -ForegroundColor Green
Write-Host ""
Write-Host "  App (CloudFront) : $CfUrl"
Write-Host "  API health       : $HealthUrl"
Write-Host ("  API metrics      : {0}/api/metrics" -f $CfUrl)
Write-Host ("  API predict      : {0}/api/predict" -f $CfUrl)
Write-Host ""
Write-Host 'Tear down when finished:  .\scripts\destroy.ps1'
