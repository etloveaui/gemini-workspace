# Claude Code Integration Script for Multi-Agent Workspace
# Created: 2025-08-17
# Purpose: Integrate Claude Code into the existing Gemini + Codex workflow

param(
    [string]$Command = "",
    [switch]$Help,
    [switch]$Status,
    [switch]$Setup,
    [switch]$Test
)

# Set environment for Claude Code
$env:ACTIVE_AGENT = "claude"
$env:PYTHONIOENCODING = "utf-8"
$env:AI_REC_AUTO = "1"  # Enable automatic recording

# Workspace root
$WorkspaceRoot = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

# Colors for output
$Green = "`e[32m"
$Blue = "`e[34m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "${Color}${Message}${Reset}"
}

function Show-Help {
    Write-ColorOutput "🤖 Claude Code Integration for Multi-Agent Workspace" $Blue
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\claude.ps1 [command] [options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  /think `"query`"    - Claude thinking mode"
    Write-Host "  /code `"task`"      - Claude coding mode"
    Write-Host "  /long `"request`"   - Claude long-form response"
    Write-Host "  /fast `"quick`"     - Claude fast response"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Status            - Show integration status"
    Write-Host "  -Setup             - Run initial setup"
    Write-Host "  -Test              - Test integration"
    Write-Host "  -Help              - Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\claude.ps1 /think `"Analyze this workspace structure`""
    Write-Host "  .\claude.ps1 -Status"
    Write-Host "  .\claude.ps1 -Setup"
}

function Test-Integration {
    Write-ColorOutput "🔍 Testing Claude Code Integration..." $Blue
    
    # Test Python integration script
    if (Test-Path "$WorkspaceRoot\scripts\claude_integration.py") {
        Write-ColorOutput "✅ Integration script found" $Green
        
        try {
            $output = python "$WorkspaceRoot\scripts\claude_integration.py"
            Write-ColorOutput "Integration test results:" $Blue
            Write-Host $output
        }
        catch {
            Write-ColorOutput "❌ Integration test failed: $_" $Red
        }
    } else {
        Write-ColorOutput "❌ Integration script not found" $Red
    }
}

function Show-Status {
    Write-ColorOutput "📊 Claude Code Integration Status" $Blue
    Write-Host ""
    
    # Check key files
    $KeyFiles = @(
        "CLAUDE.md",
        "scripts\claude_integration.py",
        "docs\HUB.md",
        ".agents\config.json"
    )
    
    foreach ($file in $KeyFiles) {
        $path = Join-Path $WorkspaceRoot $file
        if (Test-Path $path) {
            Write-ColorOutput "✅ $file" $Green
        } else {
            Write-ColorOutput "❌ $file" $Red
        }
    }
    
    Write-Host ""
    Write-ColorOutput "🏠 Workspace: $WorkspaceRoot" $Blue
    Write-ColorOutput "🤖 Active Agent: $env:ACTIVE_AGENT" $Blue
    Write-ColorOutput "🎯 Encoding: $env:PYTHONIOENCODING" $Blue
}

function Run-Setup {
    Write-ColorOutput "⚙️ Setting up Claude Code Integration..." $Blue
    
    # Ensure directories exist
    $RequiredDirs = @(
        ".agents",
        "docs",
        "scripts",
        "terminal_logs",
        "agents_hub\queue",
        "agents_hub\processing\claude",
        "agents_hub\archive"
    )
    
    foreach ($dir in $RequiredDirs) {
        $path = Join-Path $WorkspaceRoot $dir
        if (-not (Test-Path $path)) {
            New-Item -Path $path -ItemType Directory -Force | Out-Null
            Write-ColorOutput "📁 Created: $dir" $Green
        }
    }
    
    # Set Claude as active agent
    $agentConfig = @{
        active = "claude"
        last_updated = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
    }
    
    $configPath = Join-Path $WorkspaceRoot ".agents\config.json"
    $agentConfig | ConvertTo-Json | Set-Content -Path $configPath -Encoding UTF8
    Write-ColorOutput "🎯 Set Claude as active agent" $Green
    
    # Test integration
    Test-Integration
    
    Write-ColorOutput "✅ Claude Code integration setup complete!" $Green
}

function Invoke-ClaudeCode {
    param([string]$Mode, [string]$Query)
    
    Write-ColorOutput "🤖 Claude Code: $Mode" $Blue
    Write-ColorOutput "📝 Query: $Query" $Yellow
    
    # Set up recording if enabled
    if ($env:AI_REC_AUTO -eq "1") {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $logDir = Join-Path $WorkspaceRoot "terminal_logs\$(Get-Date -Format 'yyyy-MM-dd')"
        if (-not (Test-Path $logDir)) {
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        }
        
        $transcriptFile = Join-Path $logDir "claude_session_${timestamp}.txt"
        Start-Transcript -Path $transcriptFile -Append
        Write-ColorOutput "📹 Recording session to: $transcriptFile" $Blue
    }
    
    # This is where Claude Code would be invoked
    # For now, we'll use a placeholder that integrates with the existing system
    Write-ColorOutput "🔄 Integrating with Multi-Agent Workspace..." $Yellow
    
    # Log to usage tracking (if available)
    if (Test-Path "$WorkspaceRoot\scripts\usage_tracker.py") {
        try {
            python "$WorkspaceRoot\scripts\usage_tracker.py" log_usage "claude" "$Mode" "query='$Query'"
        }
        catch {
            Write-ColorOutput "⚠️ Could not log usage: $_" $Yellow
        }
    }
    
    # In a real implementation, this would call Claude Code CLI
    Write-ColorOutput "💭 This would call Claude Code with: $Query" $Green
    Write-ColorOutput "🔗 Mode: $Mode" $Green
    Write-ColorOutput "🏠 Workspace: $WorkspaceRoot" $Green
    
    # Stop transcript if it was started
    if ($env:AI_REC_AUTO -eq "1") {
        Stop-Transcript
    }
}

# Main script logic
try {
    Set-Location $WorkspaceRoot
    
    if ($Help) {
        Show-Help
        exit 0
    }
    
    if ($Status) {
        Show-Status
        exit 0
    }
    
    if ($Setup) {
        Run-Setup
        exit 0
    }
    
    if ($Test) {
        Test-Integration
        exit 0
    }
    
    # Parse Claude Code commands
    if ($Command -match '^/(think|code|long|fast)\s+(.+)$') {
        $mode = $matches[1]
        $query = $matches[2].Trim('"')
        Invoke-ClaudeCode -Mode $mode -Query $query
    }
    elseif ($Command) {
        Write-ColorOutput "❌ Unknown command: $Command" $Red
        Write-ColorOutput "Use -Help to see available commands" $Yellow
    }
    else {
        Show-Help
    }
}
catch {
    Write-ColorOutput "❌ Error: $_" $Red
    exit 1
}