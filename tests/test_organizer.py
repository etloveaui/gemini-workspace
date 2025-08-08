# tests/test_organizer.py
import pytest
from pathlib import Path
from scripts.organizer import ScratchpadOrganizer

@pytest.fixture
def scratchpad(tmp_path: Path) -> Path:
    """테스트용 가상 scratchpad 디렉터리 및 파일 생성"""
    sp_dir = tmp_path / "scratchpad"
    sp_dir.mkdir()
    # 테스트 케이스 파일들
    (sp_dir / "20250808_daily_report.log").write_text("일일 작업 로그")
    (sp_dir / "[P2-UX]_Final_Plan.md").write_text("프로젝트 최종 계획서")
    (sp_dir / "debug_output.txt").write_text("Exception: Null pointer")
    (sp_dir / "LLM_response_01.json").write_text('{"user": "Hi", "assistant": "Hello"}')
    (sp_dir / "misc_notes.txt").write_text("Just some random notes")
    (sp_dir / "sub").mkdir()
    (sp_dir / "sub" / "patch_note.txt").write_text("hotfix patch")
    # 이름 충돌 테스트용 파일
    (sp_dir / "1_daily_logs").mkdir()
    (sp_dir / "1_daily_logs" / "20250808_daily_report.log").write_text("existing file")
    # 이미 분류된 파일 (멱등성 테스트용)
    (sp_dir / "_archive").mkdir()
    (sp_dir / "_archive" / "old_backup.zip").touch()
    return sp_dir

def test_classification_logic(scratchpad):
    """핵심 분류 로직이 의도대로 동작하는지 점검"""
    organizer = ScratchpadOrganizer(str(scratchpad))
    assert organizer._pick_category(organizer._score_file(scratchpad / "20250808_daily_report.log", "")) == "1_daily_logs"
    assert organizer._pick_category(organizer._score_file(scratchpad / "[P2-UX]_Final_Plan.md", "")) == "2_proposals_and_plans"
    assert organizer._pick_category(organizer._score_file(scratchpad / "debug_output.txt", "Exception")) == "3_debug_and_tests"
    assert organizer._pick_category(organizer._score_file(scratchpad / "sub" / "patch_note.txt", "")) == "3_debug_and_tests"
    assert organizer._pick_category(organizer._score_file(scratchpad / "LLM_response_01.json", "Assistant:")) == "4_llm_io"
    assert organizer._pick_category(organizer._score_file(scratchpad / "misc_notes.txt", "")) == "_archive"

def test_idempotency_and_move_plan(scratchpad):
    """이미 분류된 파일은 제외하고 이동 계획을 생성하는지 테스트"""
    organizer = ScratchpadOrganizer(str(scratchpad))
    organizer.generate_move_plan()
    # 총 8개 파일/디렉터리 중, 정리 대상 파일은 5개여야 함
    # (디렉터리 3개, 이미 분류된 파일 1개 제외)
    assert len(organizer.move_plan) == 5

def test_end_to_end_execution_with_collision(scratchpad):
    """이름 충돌을 포함한 전체 실행 흐름 테스트"""
    organizer = ScratchpadOrganizer(str(scratchpad), dry_run=False, auto_yes=True)
    organizer.run()

    # 1. 원본 파일이 이동되었는지 확인
    assert not (scratchpad / "[P2-UX]_Final_Plan.md").exists()
    assert (scratchpad / "2_proposals_and_plans" / "[P2-UX]_Final_Plan.md").exists()

    # 2. 이름 충돌이 발생한 파일은 `_1` 접미사를 가져야 함
    dest_dir = scratchpad / "1_daily_logs"
    assert (dest_dir / "20250808_daily_report.log").exists()
    assert (dest_dir / "20250808_daily_report_1.log").exists()
    
    # 3. 로그와 저널 파일이 생성되었는지 확인
    assert (scratchpad / "organize_log.txt").exists()
    assert (scratchpad / "organize_journal.jsonl").exists()

def test_user_cancellation(scratchpad, monkeypatch):
    """사용자가 'n'을 입력했을 때 작업이 취소되는지 테스트"""
    monkeypatch.setattr('rich.prompt.Confirm.ask', lambda *args, **kwargs: False)
    
    organizer = ScratchpadOrganizer(str(scratchpad), dry_run=False, auto_yes=False)
    organizer.run()

    # 파일들이 전혀 이동되지 않았는지 확인
    assert (scratchpad / "debug_output.txt").exists()
    assert not (scratchpad / "3_debug_and_tests" / "debug_output.txt").exists()
