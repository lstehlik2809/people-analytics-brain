# One-command update of the second brain after publishing new blog posts.
# Usage: .\update.ps1            (convert + embed + llms + sync + commit + push)
#        .\update.ps1 -NoPush   (everything except commit/push)
param([switch]$NoPush)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "== 1/4 Converting new/changed posts ==" -ForegroundColor Cyan
python pipeline/convert.py
if ($LASTEXITCODE) { exit 1 }

Write-Host "== 2/4 Embedding + relinking ==" -ForegroundColor Cyan
python pipeline/embed_link.py
if ($LASTEXITCODE) { exit 1 }

Write-Host "== 3/3 Building llms.txt ==" -ForegroundColor Cyan
python pipeline/build_llms.py
if ($LASTEXITCODE) { exit 1 }

if (-not $NoPush) {
    git add -A
    git commit -m "Update second brain content"
    git push
    Write-Host "Pushed - GitHub Actions will rebuild and deploy the site." -ForegroundColor Green
} else {
    Write-Host "Done (no push). Preview locally: cd site; npx quartz build -d ..\vault --serve" -ForegroundColor Green
}
