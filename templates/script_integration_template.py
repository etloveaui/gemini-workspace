# 스크립트 자동 통합 템플릿
# {script_name} 통합

import sys
from pathlib import Path

# 스크립트 경로 추가
script_path = Path(__file__).parent / "{script_name}"
if script_path.exists():
    sys.path.append(str(script_path.parent))
    
    try:
        import {module_name}
        print(f"✅ {script_name} 통합 완료")
    except Exception as e:
        print(f"⚠️ {script_name} 통합 실패: {{e}}")
