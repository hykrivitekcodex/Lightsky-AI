$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ProjectDir "..\..")
$DistDir = Join-Path $RepoRoot "dist"
$ZipPath = Join-Path $DistDir "LightskyAIPro-iOS-source.zip"

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

if (Test-Path $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

Compress-Archive -Path $ProjectDir -DestinationPath $ZipPath -Force

Write-Host "Created $ZipPath"
