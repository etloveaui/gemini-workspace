import shutil
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]

def clear_cli_state():
    # 임시 파일 삭제
    temp_files = [
        ROOT / "COMMIT_MSG.tmp",
        ROOT / "usage.db.bak" # usage.db 백업 파일
    ]
    for f in temp_files:
        if f.exists():
            try:
                os.remove(f)
                print(f"Deleted temporary file: {f}")
            except OSError as e:
                print(f"Error deleting {f}: {e}")

    # 세션 캐시 폴더 삭제 (예: .gemini/tmp)
    gemini_tmp_path = ROOT / ".gemini" / "tmp"
    if gemini_tmp_path.exists() and gemini_tmp_path.is_dir():
        try:
            shutil.rmtree(gemini_tmp_path)
            print(f"Deleted session cache directory: {gemini_tmp_path}")
        except OSError as e:
            print(f"Error deleting {gemini_tmp_path}: {e}")

    print("CLI state cleared.")

if __name__ == "__main__":
    clear_cli_state()
