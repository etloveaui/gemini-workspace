

import sys
from pathlib import Path

# Add project root to the Python path to allow importing from 'scripts'
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from scripts.hub_manager import strip_last_session_block, HUB_PATH

def debug_stripper():
    """
    Reads the HUB.md file, applies the stripping function,
    and prints the result to verify its operation directly.
    """
    print(f"--- Reading content from: {HUB_PATH} ---")
    original_content = HUB_PATH.read_text(encoding="utf-8")
    
    print("\n--- Original Content (last 300 chars) ---")
    print(original_content[-300:])
    
    print("\n--- Applying strip_last_session_block() ---")
    stripped_content = strip_last_session_block(original_content)
    
    print("\n--- Stripped Content (last 300 chars) ---")
    print(stripped_content[-300:])
    
    print("\n--- Verification ---")
    if "__lastSession__" in stripped_content:
        print("FAILURE: '__lastSession__' block was NOT removed.")
    else:
        print("SUCCESS: '__lastSession__' block was removed.")

if __name__ == "__main__":
    debug_stripper()

