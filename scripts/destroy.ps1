<#
.SYNOPSIS
  Tear down the AWS inference backend (terraform destroy).

.DESCRIPTION
  Removes artifacts S3, Lambda + Function URL, and IAM. Does NOT delete the
  external model bucket. Frontend on Vercel is unmanaged by this script.

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

Write-Host "ECG-AI - AWS backend destroy"
Write-Host "  This removes the artifacts S3 bucket, Lambda, Function URL, and IAM"
Write-Host "  created by Terraform. The external model bucket and Vercel frontend"
Write-Host "  are left untouched."
Write-Host ""

if (-not $Yes) {
  $confirm = Read-Host "Type 'yes' to destroy the backend"
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
Write-Host "Destroy succeeded. AWS backend is gone." -ForegroundColor Green
Write-Host "Redeploy anytime with:  .\scripts\deploy.ps1"
