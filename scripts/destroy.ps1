<#
.SYNOPSIS
  One-command teardown of the portfolio demo environment (terraform destroy).

.DESCRIPTION
  Removes everything Terraform manages (frontend S3, artifacts S3, CloudFront,
  Lambda + Function URL, IAM). Does NOT delete the external model bucket.

.PARAMETER Yes
  Skip the interactive confirmation (for scripted demos).
#>
param(
  [switch]$Yes
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Infra = Join-Path $Root "infra"

if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
  throw "Required command not found on PATH: terraform"
}

Write-Host "ECG AI - portfolio destroy"
Write-Host "  This removes CloudFront, frontend/artifacts S3 buckets, Lambda, and IAM"
Write-Host "  created by Terraform. The external model bucket is left untouched."
Write-Host ""

if (-not $Yes) {
  $confirm = Read-Host "Type 'yes' to destroy the demo environment"
  if ($confirm -ne "yes") {
    Write-Host "Aborted."
    exit 0
  }
}

Push-Location $Infra
try {
  if (-not (Test-Path ".terraform")) {
    & terraform init -input=false -reconfigure
    if ($LASTEXITCODE -ne 0) { throw "terraform init failed" }
  }

  & terraform destroy -auto-approve -input=false -refresh=true
  if ($LASTEXITCODE -ne 0) { throw "terraform destroy failed (exit $LASTEXITCODE)" }
}
finally {
  Pop-Location
}

Write-Host ""
Write-Host "Destroy succeeded. Demo environment is gone." -ForegroundColor Green
Write-Host "Redeploy anytime with:  .\scripts\deploy.ps1"
