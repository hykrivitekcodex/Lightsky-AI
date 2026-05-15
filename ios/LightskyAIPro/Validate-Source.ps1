$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Validator = Join-Path $ProjectDir "scripts\validate_ios_project.py"

Write-Host "Lightsky AI Pro iOS source check"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -X utf8 $Validator
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $Validator
} else {
    throw "Python was not found. Install Python or run this from a shell where py/python is available."
}
