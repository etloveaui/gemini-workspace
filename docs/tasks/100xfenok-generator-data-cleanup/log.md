# [Project] - 100xFenok-generator 프로젝트 자료 정리

## 2025-07-22

### [Initial Analysis & Future Plan] - `scratchpad` 폴더 파일 분석 및 처리 계획

- **Context:** `C:\Users\etlov\gemini-workspace\scratchpad` 폴더 내 임시 파일 및 디렉토리들을 분석하고, `100xFenok-generator Project`의 일관된 자료 관리 및 `scratchpad` 정리.

- **Analysis Results:**
    - `scratchpad/통합JSON`:
        - `Instruction_Json.md`: JSON 데이터 가공 및 통합 지침.
        - `*.json` 파일: `main_generator.py`에서 생성된 통합 JSON 데이터.
    - `scratchpad/inputdata`:
        - `10_100x_Daily_Wrap_My_Sources_*.pdf`, `21_100x_Daily_Wrap_Prompt_*.md`, `21_100x_Daily_Wrap_Prompt_*.pdf`.
        - `main_generator.py`의 입력 데이터로 사용됨.
    - `scratchpad/Lexi_Convert`:
        - `part1`, `part2` 하위 디렉토리.
        - `Python_Lexi_Convert` 프로젝트와 관련.

- **Comprehensive Plan for `scratchpad` Cleanup (Future Execution):**
    1.  `C:\Users\etlov\gemini-workspace\scratchpad\inputdata` 내의 모든 파일을 `C:\Users\etlov\gemini-workspace\projects\100xFenok-generator\input_data`로 이동합니다.
    2.  `C:\Users\etlov\gemini-workspace\scratchpad\통합JSON\Instruction_Json.md` 파일을 `C:\Users\etlov\gemini-workspace\projects\100xFenok-generator\docs\Instruction_Json.md` (또는 `config` 폴더)로 이동하고, `main_generator.py`의 `self.integrated_json_instruction_file` 경로를 업데이트합니다.
    3.  `C:\Users\etlov\gemini-workspace\scratchpad\통합JSON` 내의 `*.json` 파일들을 `C:\Users\etlov\gemini-workspace\projects\100xFenok-generator\generated_json`으로 이동합니다.
    4.  `C:\Users\etlov\gemini-workspace\scratchpad\통합JSON` 폴더를 삭제합니다.
    5.  `C:\Users\etlov\gemini-workspace\scratchpad\Lexi_Convert` 폴더를 삭제합니다.
    6.  `C:\Users\etlov\gemini-workspace\scratchpad\inputdata` 폴더를 삭제합니다.

- **Status:** Plan Documented. Execution Pending.
