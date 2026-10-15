$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --noconsole `
    --name EnglishQuiz `
    main.py

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Output "Build complete: $PSScriptRoot\dist\EnglishQuiz.exe"
