
# 분석 요청서: GitHub Actions 워크플로우 최적화

## 1. 분석 대상
- `.github/workflows/ci.yml`
- `.github/workflows/gemini-cli.yml`

## 2. 현황 및 문제점
- **현황**: 현재 2개의 GitHub Actions 워크플로우가 CI 및 원격 AI 지원을 담당하고 있습니다.
- **분석 결과 발견된 잠재적 문제점**:
    1. **오래되거나 비공식적인 액션 사용**: `ci.yml`의 Gitleaks 스캔 액션(`gacts/gitleaks@v1`)과 `gemini-cli.yml`의 Gemini CLI 액션(`run-gemini-cli@v0`)이 최신 버전이 아닙니다. 이는 최신 기능 누락 및 보안 취약점으로 이어질 수 있습니다.
    2. **품질 게이트 부재**: `ci.yml`에 테스트는 포함되어 있으나, `GEMINI.md`에서 권장하는 정적 분석(예: `ruff`) 단계가 없어 코드 품질을 사전에 검증하는 데 한계가 있습니다.
    3. **OS 환경 불일치**: `ci.yml`은 `windows-latest`에서 실행되지만, `gemini-cli.yml`은 `ubuntu-latest`에서 실행됩니다. 프로젝트의 "Windows-first" 원칙과 어긋나며, OS 차이로 인한 미묘한 버그를 유발할 수 있습니다.
    4. **버전 관리 불명확성**: `gemini-cli.yml`에서 일부 액션이 특정 커밋 해시로 고정되어 있어 버전 관리가 불명확하고, 최신 버전 추적이 어렵습니다.

## 3. 분석 목표
- 워크플로우의 **보안성, 효율성, 유지보수성**을 개선합니다.
- CI 과정에 정적 분석을 추가하여 코드 품질을 향상시킵니다.
- 프로젝트의 표준 운영 환경(Windows)과 워크플로우 환경을 일치시켜 잠재적인 오류를 줄입니다.
- 모든 액션을 최신 안정 버전으로 업데이트하여 관리 효율성을 높입니다.

## 4. 요청 사항
- 상기 분석 목표를 달성하기 위한 구체적인 **"작업 지시서"**를 요청합니다.
- 지시서에는 다음 개선안에 대한 구체적인 실행 계획이 명시되기를 기대합니다.
    1. **`ci.yml` 개선**:
        - `gacts/gitleaks@v1`을 공식 `gitleaks/gitleaks-action@v2`로 교체합니다.
        - `pytest` 실행 후 `ruff check .` 명령을 실행하는 정적 분석 단계를 추가합니다.
    2. **`gemini-cli.yml` 개선**:
        - `google-github-actions/run-gemini-cli@v0`를 `v1`으로 업데이트합니다.
        - `actions/create-github-app-token` 및 `actions/checkout`의 버전을 명확한 최신 태그로 변경하는 것을 검토합니다.
        - `runs-on`을 `windows-latest`로 변경하고, 내부 스크립트가 Windows 환경과 호환되는지 검증합니다.
