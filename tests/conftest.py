import pytest
import os
from pathlib import Path

@pytest.fixture(scope="function")
def clean_usage_db(tmp_path):
    """테스트 전후 usage.db 파일을 정리하고 임시 경로를 반환"""
    temp_db_path = tmp_path / "usage.db"
    yield temp_db_path
    if temp_db_path.exists():
        try:
            os.remove(temp_db_path)
        except PermissionError:
            pass # Ignore if file is in use