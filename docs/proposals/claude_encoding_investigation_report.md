# 인코딩 조사 결과 보고서

## 문제 원인
- **주요 원인**: 파일 인코딩과 시스템/도구 설정 간의 불일치입니다. 한글이 포함된 파일들(`docs/HUB.md` 등)이 시스템 기본 인코딩인 `CP949`로 저장되는 반면, `.gitattributes` 설정은 해당 파일들을 `UTF-8`로 강제하고 있어 충돌이 발생합니다.
- **부차적 요인**: PowerShell의 기본 출력 인코딩이 `US-ASCII`로 설정되어 있어, 인코딩 문제를 파악하기 어렵게 만들고 잠재적인 오류를 유발할 수 있습니다.

## 현재 상태
- **시스템 기본 인코딩**: `CP949` (한글 Windows 기본)
- **문제 파일 목록**: `docs/HUB.md`에서 한글 깨짐이 확인되었습니다. 다른 한글 포함 파일들도 동일한 위험에 노출되어 있습니다.
- **Git 설정 상태**:
    - `.gitattributes`에서 `*.md` 파일에 `working-tree-encoding=UTF-8`을 강제하고 있어, 실제 `CP949`로 저장된 파일과 충돌합니다.
    - `git config`에서 `core.autocrlf`가 `true`와 `false`로 중복 설정되어 혼란을 야기합니다.
    - `i18n.commitencoding`은 `utf-8`로 올바르게 설정되어 있습니다.

## 권장 해결책
1.  **즉시 적용 가능한 해결책**: 문제가 되는 모든 파일을 **UTF-8 with BOM**으로 변환해야 합니다. BOM(Byte Order Mark)은 파일 인코딩을 명시적으로 만들어 모든 도구가 정확하게 파일을 해석하도록 합니다.
2.  **중장기 개선 방안**: 모든 에이전트(Claude, Codex, Gemini)가 파일을 저장할 때 기본적으로 `UTF-8` 인코딩을 사용하도록 설정을 통일해야 합니다.
3.  **예방 조치**: `pre-commit hook`에 파일 인코딩을 검사하는 로직을 추가하여, `UTF-8`이 아닌 파일의 커밋을 사전에 방지해야 합니다.

## 다음 단계
- **Claude에게 전달할 구체적 수정 지시사항**:
  - 다음 PowerShell 명령어를 사용하여 주요 문서 파일들을 `UTF-8 with BOM`으로 변환하세요.
    ```powershell
    $files = "docs/HUB.md", "AGENTS.md", "GEMINI.md", "CLAUDE.md";
    foreach ($file in $files) {
      $content = Get-Content $file -Encoding Default;
      Set-Content -Path $file -Value $content -Encoding UTF8 -Force -NoNewline;
      Write-Host "$file has been converted to UTF-8 with BOM."
    }
    ```
  - 위 명령어 실행 후, Git 상태를 확인하고 변경된 파일들을 커밋하여 인코딩 문제를 해결하세요.
