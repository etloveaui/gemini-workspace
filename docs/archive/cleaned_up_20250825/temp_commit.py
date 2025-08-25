import subprocess
from pathlib import Path
import tempfile
import os

def python_wip_commit_staged(message: str, cwd: Path):
    cwd = cwd.resolve()
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
        tf.write(message or "auto WIP commit")
        tf.flush()
        temp_path = tf.name

    try:
        subprocess.run(["git", "commit", "-F", temp_path], cwd=str(cwd), check=True, text=True)
    finally:
        os.unlink(temp_path)

python_wip_commit_staged("docs(gemini): clarify invoke usage and add doc update policy", Path.cwd())
