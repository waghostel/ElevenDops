# verify--gcp-migration.ps1
# This script verifies your local environment for migration to real GCP services
# and optionally starts the servers.

param(
    [int]$FastAPIPort = 8000,
    [int]$StreamlitPort = 8501
)

function Write-Step {
    param([string]$Message)
    Write-Host "`n--- $Message ---" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Kill-ProcessOnPort {
    param([int]$Port)
    Write-Host "🔍 Checking port $Port..." -ForegroundColor Blue
    $netstatOutput = netstat -ano | Select-String ":$Port "
    if ($netstatOutput) {
        Write-Host "⚠️  Found processes on port $Port. Cleaning up..." -ForegroundColor Yellow
        foreach ($line in $netstatOutput) {
            if ($line -match "\s+(\d+)$") {
                $processId = $matches[1]
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Seconds 1
    }
}

Write-Host "Elevendops GCP Migration Verifier & Launcher" -ForegroundColor Yellow -BackgroundColor Blue

# 1. Parse .env
Write-Step "Checking .env configuration..."
if (-not (Test-Path ".env")) {
    Write-Error-Custom ".env file not found."
    exit 1
}

$envContent = Get-Content ".env"
$config = @{}
foreach ($line in $envContent) {
    if ($line -match "^([^=]+)=([^#]*)(#.*)?$") {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $config[$key] = $value
    }
}

# 2. Verify Emulator Flags
Write-Step "Verifying emulator settings..."
$failed = $false
$requiredOff = @("USE_FIRESTORE_EMULATOR", "USE_GCS_EMULATOR")
foreach ($flag in $requiredOff) {
    if ($config[$flag] -eq "false") {
        Write-Success "$flag is set to false."
    }
    else {
        Write-Error-Custom "$flag should be 'false'. Current: $($config[$flag])"
        $failed = $true
    }
}

# 3. Verify IDs and Bucket
Write-Step "Verifying Project and Bucket names..."
$projectId = $config["GOOGLE_CLOUD_PROJECT"]
$bucketName = $config["GCS_BUCKET_NAME"]

if ($projectId -and $projectId -notmatch "\[.*\]") { Write-Success "Project ID: $projectId" } else { Write-Error-Custom "GOOGLE_CLOUD_PROJECT missing."; $failed = $true }
if ($bucketName -and $bucketName -notmatch "\[.*\]") { Write-Success "Bucket Name: $bucketName" } else { Write-Error-Custom "GCS_BUCKET_NAME missing."; $failed = $true }

# 4. gcloud Status
Write-Step "Checking gcloud authentication..."
$gcloudAuth = gcloud auth list --format="value(account)" --filter="status=ACTIVE"
if ($gcloudAuth) { Write-Success "Active account: $gcloudAuth" } else { Write-Error-Custom "Run 'gcloud auth login'."; $failed = $true }

$currentProject = gcloud config get-value project 2>$null
if ($currentProject -eq $projectId) { Write-Success "Project matches: $currentProject" } else { Write-Error-Custom "Project mismatch."; $failed = $true }

# 5. Resource Accessibility
Write-Step "Testing accessibility to GCP resources..."
gsutil ls "gs://$bucketName/" >$null 2>$null
if ($LASTEXITCODE -eq 0) { Write-Success "GCS Bucket accessible." } else { Write-Error-Custom "Cannot access GCS Bucket."; $failed = $true }

# 6. Firestore Connectivity
Write-Step "Testing Firestore connectivity..."
$firestoreDbId = $config["FIRESTORE_DATABASE_ID"]
if (-not $firestoreDbId) { $firestoreDbId = "(default)" }

$firestoreCheck = gcloud firestore databases describe --database="$firestoreDbId" --project="$projectId" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Firestore database '$firestoreDbId' accessible."
} else {
    Write-Error-Custom "Cannot access Firestore database '$firestoreDbId'."
    Write-Host "  Hint: Ensure the database exists in project '$projectId'." -ForegroundColor Yellow
    Write-Host "  Create with: gcloud firestore databases create --location=us-central1 --database=$firestoreDbId --project=$projectId" -ForegroundColor Yellow
    $failed = $true
}

if ($failed) {
    Write-Host "`n--- Verification FAILED ---" -ForegroundColor Red
    exit 1
}

Write-Host "`n--- Verification SUCCESS ---" -ForegroundColor Green
$choice = Read-Host "Would you like to start the servers now? (Y/N)"
if ($choice -ne "Y") { exit 0 }

# 7. Start Servers
Write-Step "Starting Servers..."
Kill-ProcessOnPort -Port $FastAPIPort
Kill-ProcessOnPort -Port $StreamlitPort

$envGoogleApiKey = $config["GOOGLE_API_KEY"]
$envElevenLabsKey = $config["ELEVENLABS_API_KEY"]

Write-Host "🚀 Launching FastAPI..." -ForegroundColor Blue
$fastApiJob = Start-Job -ScriptBlock {
    param($port, $proj, $bucket, $googleKey, $elevenKey)
    Set-Location $using:PWD
    [Environment]::SetEnvironmentVariable("GOOGLE_CLOUD_PROJECT", $proj, "Process")
    [Environment]::SetEnvironmentVariable("GCS_BUCKET_NAME", $bucket, "Process")
    [Environment]::SetEnvironmentVariable("USE_FIRESTORE_EMULATOR", "false", "Process")
    [Environment]::SetEnvironmentVariable("USE_GCS_EMULATOR", "false", "Process")
    [Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $googleKey, "Process")
    [Environment]::SetEnvironmentVariable("ELEVENLABS_API_KEY", $elevenKey, "Process")
    uv run uvicorn backend.main:app --host localhost --port $port
} -ArgumentList $FastAPIPort, $projectId, $bucketName, $envGoogleApiKey, $envElevenLabsKey

Write-Host "🚀 Launching Streamlit..." -ForegroundColor Blue
$streamlitJob = Start-Job -ScriptBlock {
    param($port)
    Set-Location $using:PWD
    uv run streamlit run streamlit_app/app.py --server.port $port --server.address localhost
} -ArgumentList $StreamlitPort

# Save job IDs for stop_server.ps1 compatibility
$jobIds = @{
    FastAPI       = $fastApiJob.Id
    Streamlit     = $streamlitJob.Id
    FastAPIPort   = $FastAPIPort
    StreamlitPort = $StreamlitPort
}
$jobIds | ConvertTo-Json | Out-File -FilePath ".server_jobs.json" -Encoding UTF8

Write-Host "`n✅ Servers are starting in the background!" -ForegroundColor Green
Write-Host "👉 FastAPI: http://localhost:$FastAPIPort" -ForegroundColor Cyan
Write-Host "👉 Streamlit: http://localhost:$StreamlitPort" -ForegroundColor Cyan
Write-Host "`nTo stop servers, run: .\stop_server.ps1" -ForegroundColor Yellow
