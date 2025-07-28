import sys
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NO_DELETE_LIST_PATH = ROOT / ".no_delete_list"

def check_no_delete():
    if not NO_DELETE_LIST_PATH.exists():
        return

    with open(NO_DELETE_LIST_PATH, 'r', encoding='utf-8') as f:
        protected_paths = [Path(line.strip()) for line in f if line.strip() and not line.startswith('#')]

    if not protected_paths:
        return

    # Get staged changes
    try:
        diff_output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-status"],
            cwd=ROOT,
            text=True,
            encoding='utf-8'
        ).strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e}", file=sys.stderr)
        sys.exit(1)

    deleted_or_renamed_files = []
    for line in diff_output.splitlines():
        status, *paths = line.split('\t')
        current_path = Path(paths[-1]) # For R (rename), the last path is the new path

        if status.startswith('D') or status.startswith('R'): # D: deleted, R: renamed
            # For renamed files, check both old and new paths
            if status.startswith('R') and len(paths) == 2:
                old_path = Path(paths[0])
                if old_path in protected_paths:
                    deleted_or_renamed_files.append(old_path)
            
            if current_path in protected_paths:
                deleted_or_renamed_files.append(current_path)

    if deleted_or_renamed_files:
        print("ERROR: The following protected files are being deleted or renamed:", file=sys.stderr)
        for p in deleted_or_renamed_files:
            print(f"- {p}", file=sys.stderr)
        print("Commit aborted. Please revert these changes or remove them from .no_delete_list if intentional.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    check_no_delete()
