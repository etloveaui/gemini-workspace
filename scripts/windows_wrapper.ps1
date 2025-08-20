# 🖥️ Windows 환경 표준화 래퍼 v1.0
# 멀티 에이전트 워크스페이스용 Windows 경로/인용 문제 해결

<#
.SYNOPSIS
Windows 환경에서 멀티 에이전트 워크스페이스의 일반적인 문제를 해결하는 래퍼

.DESCRIPTION
- PowerShell/CMD 간 인용 규칙 차이 해결
- 경로 구분자 자동 변환
- 한글 파일명 처리
- Git 커밋 메시지 인코딩 문제 해결

.EXAMPLE
.\scripts\windows_wrapper.ps1 -Command "git-commit" -Message "한글 커밋 메시지"
.\scripts\windows_wrapper.ps1 -Command "invoke-task" -TaskName "start"
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("git-commit", "invoke-task", "python-run", "path-convert", "encoding-check")]
    [string]$Command,
    
    [Parameter()]
    [string]$Message,
    
    [Parameter()]  
    [string]$TaskName,
    
    [Parameter()]
    [string]$PythonScript,
    
    [Parameter()]
    [string]$Path,
    
    [Parameter()]
    [switch]$Verbose
)

# 🎨 컬러 출력 함수
function Write-ColorOutput {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

# 📁 경로 정규화 함수
function ConvertTo-SafePath {
    param([string]$InputPath)
    
    if (-not $InputPath) { return "" }
    
    # Windows 경로 정규화
    $safePath = $InputPath -replace '/', '\'
    $safePath = $safePath -replace '\\+', '\'
    
    # 공백 포함된 경로는 따옴표로 감싸기
    if ($safePath -match '\s') {
        $safePath = "`"$safePath`""
    }
    
    return $safePath
}

# 🔧 인코딩 설정 함수
function Set-OptimalEncoding {
    # PowerShell 인코딩 설정
    $OutputEncoding = [System.Text.UTF8Encoding]::new()
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new()
    
    # 환경 변수 설정
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    
    if ($Verbose) {
        Write-ColorOutput "✅ 인코딩 설정 완료 (UTF-8)" "Green"
    }
}

# 🎯 메인 명령어 처리
switch ($Command) {
    "git-commit" {
        Write-ColorOutput "🔧 Git 커밋 (Windows 안전 모드)" "Cyan"
        Set-OptimalEncoding
        
        if (-not $Message) {
            Write-ColorOutput "❌ 커밋 메시지가 필요합니다" "Red"
            exit 1
        }
        
        try {
            # 임시 파일로 커밋 메시지 처리 (CLAUDE.md 방식)
            $tempFile = "COMMIT_MSG_TEMP.tmp"
            $Message | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
            
            git add . 
            git commit -F $tempFile
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✅ 커밋 성공" "Green"
                Remove-Item $tempFile -ErrorAction SilentlyContinue
                
                # Push 여부 확인
                $pushResponse = Read-Host "📤 원격 저장소에 푸시하시겠습니까? (y/n)"
                if ($pushResponse -eq 'y' -or $pushResponse -eq 'Y') {
                    git push
                    if ($LASTEXITCODE -eq 0) {
                        Write-ColorOutput "✅ 푸시 성공" "Green"
                    }
                }
            } else {
                Write-ColorOutput "❌ 커밋 실패" "Red"
                Remove-Item $tempFile -ErrorAction SilentlyContinue
                exit 1
            }
        }
        catch {
            Write-ColorOutput "❌ Git 커밋 중 오류: $_" "Red"
            Remove-Item $tempFile -ErrorAction SilentlyContinue -Force
            exit 1
        }
    }
    
    "invoke-task" {
        Write-ColorOutput "⚡ Invoke 태스크 실행 (Windows 안전 모드)" "Cyan"
        Set-OptimalEncoding
        
        if (-not $TaskName) {
            Write-ColorOutput "❌ 태스크명이 필요합니다" "Red"
            exit 1
        }
        
        try {
            # Python 가상환경 확인
            if ($env:VIRTUAL_ENV -or (python -c "import sys; print(sys.prefix != sys.base_prefix)" 2>$null) -eq "True") {
                invoke $TaskName
            } else {
                Write-ColorOutput "⚠️  가상환경이 활성화되지 않았습니다" "Yellow"
                $activateScript = "venv\Scripts\Activate.ps1"
                
                if (Test-Path $activateScript) {
                    Write-ColorOutput "🔧 가상환경 자동 활성화 시도..." "Blue"
                    & $activateScript
                    invoke $TaskName
                } else {
                    Write-ColorOutput "❌ 가상환경을 찾을 수 없습니다" "Red"
                    exit 1
                }
            }
        }
        catch {
            Write-ColorOutput "❌ Invoke 실행 중 오류: $_" "Red"
            exit 1
        }
    }
    
    "python-run" {
        Write-ColorOutput "🐍 Python 스크립트 실행 (Windows 안전 모드)" "Cyan"
        Set-OptimalEncoding
        
        if (-not $PythonScript) {
            Write-ColorOutput "❌ Python 스크립트 경로가 필요합니다" "Red"
            exit 1
        }
        
        $safePythonScript = ConvertTo-SafePath $PythonScript
        
        try {
            if (Test-Path $PythonScript) {
                python $safePythonScript
            } else {
                Write-ColorOutput "❌ 스크립트 파일을 찾을 수 없습니다: $PythonScript" "Red"
                exit 1
            }
        }
        catch {
            Write-ColorOutput "❌ Python 실행 중 오류: $_" "Red"
            exit 1
        }
    }
    
    "path-convert" {
        Write-ColorOutput "📁 경로 변환 유틸리티" "Cyan"
        
        if (-not $Path) {
            Write-ColorOutput "❌ 변환할 경로가 필요합니다" "Red"
            exit 1
        }
        
        $convertedPath = ConvertTo-SafePath $Path
        Write-ColorOutput "🔄 원본: $Path" "Yellow"
        Write-ColorOutput "✅ 변환: $convertedPath" "Green"
        
        # 클립보드에 복사 (선택사항)
        try {
            $convertedPath | Set-Clipboard
            Write-ColorOutput "📋 클립보드에 복사됨" "Blue"
        }
        catch {
            # 클립보드 복사 실패는 무시
        }
    }
    
    "encoding-check" {
        Write-ColorOutput "🔍 인코딩 환경 진단" "Cyan"
        
        Write-Host "`n📊 현재 인코딩 상태:" -ForegroundColor White
        Write-Host "  PowerShell OutputEncoding: $($OutputEncoding.EncodingName)" -ForegroundColor Gray
        Write-Host "  Console OutputEncoding: $([Console]::OutputEncoding.EncodingName)" -ForegroundColor Gray
        Write-Host "  Console InputEncoding: $([Console]::InputEncoding.EncodingName)" -ForegroundColor Gray
        Write-Host "  PYTHONIOENCODING: $($env:PYTHONIOENCODING)" -ForegroundColor Gray
        Write-Host "  PYTHONUTF8: $($env:PYTHONUTF8)" -ForegroundColor Gray
        
        # 테스트 문자열 출력
        Write-Host "`n🧪 인코딩 테스트:" -ForegroundColor White
        $testString = "테스트 한글 문자열 🎯✅❌"
        Write-Host "  $testString" -ForegroundColor Green
        
        # 최적화 제안
        Write-Host "`n💡 최적화 권장사항:" -ForegroundColor Blue
        Write-Host "  1. PowerShell 프로필에 인코딩 설정 추가" -ForegroundColor Gray
        Write-Host "  2. Git config core.quotepath false 설정" -ForegroundColor Gray
        Write-Host "  3. VSCode에서 UTF-8 인코딩 확인" -ForegroundColor Gray
        
        Set-OptimalEncoding
        Write-ColorOutput "✅ 최적 인코딩으로 설정됨" "Green"
    }
}

if ($Verbose) {
    Write-ColorOutput "`n🎯 Windows 래퍼 작업 완료" "Green"
}