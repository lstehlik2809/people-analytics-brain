# One-command update of the second brain after publishing new or changed posts.
# Usage: .\update.ps1                    (sync blog + rebuild + commit + push)
#        .\update.ps1 -NoPush            (everything except commit/push)
#        .\update.ps1 -NoPull [-NoPush]  (use the current local blog source)
param(
    [switch]$NoPush,
    [switch]$NoPull
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$BrainRoot = $PSScriptRoot
$BlogRoot = "D:\_WORKFORCE_ANALYTICS\People_Analytics_Blog"

function Get-RepoChanges([string]$RepoRoot) {
    $changes = @(git -C $RepoRoot status --porcelain)
    if ($LASTEXITCODE) { throw "Could not read git status in $RepoRoot" }
    return $changes
}

if (-not (Test-Path -LiteralPath $BlogRoot -PathType Container)) {
    throw "Blog repository not found: $BlogRoot"
}

$brainChanges = @(Get-RepoChanges $BrainRoot)
if ($brainChanges.Count -gt 0) {
    Write-Host "The second-brain worktree must be clean before updating:" -ForegroundColor Red
    $brainChanges | ForEach-Object { Write-Host "  $_" }
    throw "Commit, stash, or discard those changes before running update.ps1."
}

Write-Host "== 1/5 Synchronizing blog source ==" -ForegroundColor Cyan
if ($NoPull) {
    Write-Host "Skipped (-NoPull); using the current local blog source." -ForegroundColor Yellow
} else {
    $blogChanges = @(Get-RepoChanges $BlogRoot)
    if ($blogChanges.Count -gt 0) {
        Write-Host "The blog worktree must be clean before it can be synchronized:" -ForegroundColor Red
        $blogChanges | ForEach-Object { Write-Host "  $_" }
        throw "Commit, stash, or discard those changes, or use -NoPull intentionally."
    }
    git -C $BlogRoot pull --ff-only
    if ($LASTEXITCODE) { throw "Could not fast-forward the blog repository." }
}

Write-Host "== 2/5 Converting new/changed posts ==" -ForegroundColor Cyan
python pipeline/convert.py
if ($LASTEXITCODE) { exit 1 }

Write-Host "== 3/5 Embedding + relinking ==" -ForegroundColor Cyan
python pipeline/embed_link.py
if ($LASTEXITCODE) { exit 1 }

Write-Host "== 4/5 Building llms.txt ==" -ForegroundColor Cyan
python pipeline/build_llms.py
if ($LASTEXITCODE) { exit 1 }

Write-Host "== 5/5 Building semantic search index ==" -ForegroundColor Cyan
node pipeline/build_semantic_index.mjs
if ($LASTEXITCODE) { exit 1 }

$generatedChanges = @(Get-RepoChanges $BrainRoot)
if ($generatedChanges.Count -eq 0) {
    Write-Host "Done - the second brain is already current; nothing to commit." -ForegroundColor Green
    exit 0
}

Write-Host "Generated changes:" -ForegroundColor Cyan
$generatedChanges | ForEach-Object { Write-Host "  $_" }

if ($NoPush) {
    Write-Host "Done (no push). Preview locally: cd site; npx quartz build -d ..\vault --serve" -ForegroundColor Green
    exit 0
}

# The initial clean-worktree check makes these the only possible changes, and
# the explicit paths keep transient/ignored pipeline files out of the commit.
git add -- README.md vault pipeline/cache/manifest.json pipeline/cache/llms.txt pipeline/cache/llms-full.txt pipeline/cache/semantic_index.json
if ($LASTEXITCODE) { throw "Could not stage generated second-brain files." }

git diff --cached --quiet
$stagedDiff = $LASTEXITCODE
if ($stagedDiff -eq 0) {
    Write-Host "Done - no tracked generated changes need committing." -ForegroundColor Green
    exit 0
}
if ($stagedDiff -ne 1) { throw "Could not inspect staged changes." }

git commit -m "Update second brain content"
if ($LASTEXITCODE) { throw "Could not commit the second-brain update." }
git push
if ($LASTEXITCODE) { throw "Could not push the second-brain update." }
Write-Host "Pushed - GitHub Actions will rebuild and deploy the site." -ForegroundColor Green
