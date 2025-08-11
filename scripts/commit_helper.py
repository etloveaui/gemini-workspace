import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import subprocess


def main():
    msg = os.environ.get("COMMIT_MSG", "auto WIP commit")
    no_verify = os.environ.get("NO_VERIFY", "0") in {"1", "true", "True"}
    cwd = Path.cwd()
    if os.environ.get("SKIP_ADD") not in {"1", "true", "True"}:
        subprocess.run(["git", "add", "-A"], cwd=str(cwd), check=True, text=True)
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile('w', delete=False, encoding='utf-8') as tf:
        tf.write(msg)
        tf.flush()
        temp_path = tf.name
    try:
        cmd = ["git", "commit"]
        if no_verify:
            cmd.append("--no-verify")
        cmd.extend(["-F", temp_path])
        subprocess.run(cmd, cwd=str(cwd), check=True, text=True)
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass


if __name__ == "__main__":
    main()
