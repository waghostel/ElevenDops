# ElevenDops API Test Script
# Tests all backend API endpoints and writes results to file

$BaseUrl = "http://localhost:8000"
$Results = @()
$OutputFile = "C:\Users\Cheney\Documents\Github\ElevenDops\api_test_results.txt"

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Path,
        [string]$Description,
        [hashtable]$Body = $null
    )
    
    $url = "$BaseUrl$Path"
    $result = @{
        Endpoint = "$Method $Path"
        Description = $Description
        Status = "Unknown"
        StatusCode = 0
        Success = $false
    }
    
    try {
        if ($Method -eq "GET") {
            $response = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -TimeoutSec 10
        } elseif ($Method -eq "POST") {
            $jsonBody = $Body | ConvertTo-Json -Depth 5
            $response = Invoke-WebRequest -Uri $url -Method Post -Body $jsonBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 10
        } elseif ($Method -eq "DELETE") {
            $response = Invoke-WebRequest -Uri $url -Method Delete -UseBasicParsing -TimeoutSec 10
        }
        
        $result.StatusCode = $response.StatusCode
        $result.Success = ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300)
        $result.Status = if ($result.Success) { "PASS" } else { "FAIL" }
        $result.ResponsePreview = if ($response.Content.Length -gt 200) { $response.Content.Substring(0, 200) } else { $response.Content }
    }
    catch {
        $result.Status = "ERROR"
        $result.Error = $_.Exception.Message
        if ($_.Exception.Response) {
            $result.StatusCode = [int]$_.Exception.Response.StatusCode
        }
    }
    
    return $result
}

# Start testing
"=" * 60 | Out-File $OutputFile
"ElevenDops API Test Report" | Out-File $OutputFile -Append
"Test Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File $OutputFile -Append
"Base URL: $BaseUrl" | Out-File $OutputFile -Append
"=" * 60 | Out-File $OutputFile -Append

# Page 1: Doctor Dashboard
"`n=== PAGE 1: Doctor Dashboard ===" | Out-File $OutputFile -Append
$Results += Test-Endpoint -Method "GET" -Path "/api/health" -Description "Health Check"
$Results += Test-Endpoint -Method "GET" -Path "/api/dashboard/stats" -Description "Dashboard Stats"

# Page 2: Upload Knowledge  
"`n=== PAGE 2: Upload Knowledge ===" | Out-File $OutputFile -Append
$Results += Test-Endpoint -Method "GET" -Path "/api/knowledge" -Description "List Knowledge"

$createBody = @{
    disease_name = "PowerShell Test Disease"
    document_type = "faq"
    raw_content = "# Test FAQ\n\nQ: What is this?\nA: A test document."
}
$createResult = Test-Endpoint -Method "POST" -Path "/api/knowledge" -Description "Create Knowledge" -Body $createBody
$Results += $createResult

# Page 3: Education Audio
"`n=== PAGE 3: Education Audio ===" | Out-File $OutputFile -Append
$Results += Test-Endpoint -Method "GET" -Path "/api/audio/voices/list" -Description "Get Voices"

# Page 4: Agent Setup
"`n=== PAGE 4: Agent Setup ===" | Out-File $OutputFile -Append
$Results += Test-Endpoint -Method "GET" -Path "/api/agent" -Description "List Agents"

# Page 6: Conversation Logs
"`n=== PAGE 6: Conversation Logs ===" | Out-File $OutputFile -Append
$Results += Test-Endpoint -Method "GET" -Path "/api/conversations" -Description "List Conversations"
$Results += Test-Endpoint -Method "GET" -Path "/api/conversations/statistics" -Description "Conv Statistics"

# Write results
"`n" + "=" * 60 | Out-File $OutputFile -Append
"DETAILED RESULTS" | Out-File $OutputFile -Append
"=" * 60 | Out-File $OutputFile -Append

foreach ($r in $Results) {
    $icon = if ($r.Success) { "[PASS]" } else { "[FAIL]" }
    "$icon $($r.Endpoint) - $($r.Description)" | Out-File $OutputFile -Append
    "    Status Code: $($r.StatusCode)" | Out-File $OutputFile -Append
    if ($r.Error) {
        "    Error: $($r.Error)" | Out-File $OutputFile -Append
    }
}

# Summary
$passed = ($Results | Where-Object { $_.Success }).Count
$failed = ($Results | Where-Object { -not $_.Success }).Count
$total = $Results.Count

"`n" + "=" * 60 | Out-File $OutputFile -Append
"SUMMARY" | Out-File $OutputFile -Append
"=" * 60 | Out-File $OutputFile -Append
"Total: $total | Passed: $passed | Failed: $failed" | Out-File $OutputFile -Append
"Success Rate: $([math]::Round($passed/$total*100, 1))%" | Out-File $OutputFile -Append

# Output file path for verification
"Results written to: $OutputFile"
