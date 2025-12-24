# Kiro Shell Integration Testing Guide

This guide provides step-by-step instructions to test Kiro's shell integration capabilities on Windows systems.

## Prerequisites

- Kiro IDE installed and running
- PowerShell 7+ (recommended) or Windows PowerShell
- Basic understanding of command line operations

## Test Categories

### 1. Basic Shell Command Execution

#### Test 1.1: Simple Commands
```powershell
# Test basic echo command
echo "Hello Kiro!"

# Test system information
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion

# Test current directory
Get-Location
```

#### Test 1.2: File System Operations
```powershell
# List current directory contents
Get-ChildItem

# Create a test directory
New-Item -ItemType Directory -Name "kiro-test" -Force

# Create a test file
"This is a test file" | Out-File -FilePath "kiro-test/test.txt"

# Read the file content
Get-Content "kiro-test/test.txt"

# Clean up
Remove-Item -Recurse -Force "kiro-test"
```

### 2. Environment and System Tests

#### Test 2.1: Environment Variables
```powershell
# Check PowerShell version
$PSVersionTable

# Check execution policy
Get-ExecutionPolicy

# Display PATH environment variable
$env:PATH -split ';' | Select-Object -First 10

# Check current user
$env:USERNAME
```

#### Test 2.2: System Information
```powershell
# Check OS information
Get-WmiObject -Class Win32_OperatingSystem | Select-Object Caption, Version, Architecture

# Check available disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace

# Check running processes (top 5 by CPU)
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name, CPU, WorkingSet
```

### 3. Development Tools Integration

#### Test 3.1: Node.js and npm (if installed)
```powershell
# Check Node.js version
node --version

# Check npm version
npm --version

# List global packages
npm list -g --depth=0
```

#### Test 3.2: Python (if installed)
```powershell
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list
```

#### Test 3.3: Git (if installed)
```powershell
# Check Git version
git --version

# Check Git configuration
git config --list --global
```

### 4. Advanced Shell Features

#### Test 4.1: Piping and Filtering
```powershell
# Test piping with filtering
Get-Process | Where-Object {$_.ProcessName -like "chrome*"} | Select-Object Name, Id, CPU

# Test with sorting
Get-ChildItem C:\Windows\System32 | Sort-Object Length -Descending | Select-Object -First 5 Name, Length
```

#### Test 4.2: Error Handling
```powershell
# Test command that should fail
Get-Content "nonexistent-file.txt" 2>&1

# Test with try-catch
try {
    Get-Item "nonexistent-file.txt" -ErrorAction Stop
} catch {
    Write-Output "Expected error: File not found"
}
```

### 5. Kiro-Specific Integration Tests

#### Test 5.1: Multi-line Commands
```powershell
# Test multi-line PowerShell script
$testVar = "Kiro Integration Test"
Write-Output "Starting: $testVar"
Get-Date
Write-Output "Test completed successfully"
```

#### Test 5.2: Interactive Commands
```powershell
# Test command with output that Kiro should capture
for ($i = 1; $i -le 5; $i++) {
    Write-Output "Step $i of 5"
    Start-Sleep -Milliseconds 500
}
```

### 6. Error Scenarios and Edge Cases

#### Test 6.1: Permission Issues
```powershell
# Test accessing restricted directory (should handle gracefully)
try {
    Get-ChildItem "C:\System Volume Information" -ErrorAction Stop
} catch {
    Write-Output "Expected: Access denied to system directory"
}
```

#### Test 6.2: Long Running Commands
```powershell
# Test command that takes time (Kiro should handle appropriately)
Write-Output "Starting 10-second test..."
Start-Sleep -Seconds 10
Write-Output "Long running command completed"
```

#### Test 6.3: Large Output
```powershell
# Test command with substantial output
Get-ChildItem C:\Windows -Recurse -ErrorAction SilentlyContinue | Select-Object -First 100 Name, Length
```

## Expected Results

### Success Indicators
- [ ] All basic commands execute without errors
- [ ] File operations work correctly
- [ ] Environment variables are accessible
- [ ] System information is retrieved successfully
- [ ] Development tools are detected (if installed)
- [ ] Complex piping and filtering work
- [ ] Error handling is graceful
- [ ] Multi-line scripts execute properly
- [ ] Output is captured and displayed correctly

### Common Issues to Watch For
- Execution policy restrictions
- Path resolution problems
- Permission denied errors
- Timeout on long-running commands
- Encoding issues with special characters
- Environment variable conflicts

## Troubleshooting

### If Commands Fail
1. Check PowerShell execution policy: `Get-ExecutionPolicy`
2. Verify current working directory: `Get-Location`
3. Check if required tools are in PATH: `$env:PATH`
4. Test with simpler commands first
5. Check for project-specific restrictions

### If Output is Garbled
1. Check PowerShell encoding: `$OutputEncoding`
2. Try with different output methods
3. Verify console settings in Kiro

## Test Completion Checklist

- [ ] Basic shell commands work
- [ ] File system operations successful
- [ ] Environment detection working
- [ ] Development tools integration tested
- [ ] Advanced features functional
- [ ] Error handling appropriate
- [ ] Performance acceptable for typical use cases

## Notes

Record any issues, unexpected behaviors, or performance observations during testing:

```
Date: ___________
Tester: ___________
Kiro Version: ___________
PowerShell Version: ___________

Issues Found:
- 
- 
- 

Performance Notes:
- 
- 
- 
```