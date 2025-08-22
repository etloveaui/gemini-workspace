#!/usr/bin/env python3
"""
자동 상태 업데이트 시스템 v1.0
사용자가 신경쓰지 않아도 HUB.md와 작업 로그들이 자동으로 업데이트됩니다.
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import glob

class AutoStatusUpdater:
    def __init__(self):
        self.root = Path("C:/Users/etlov/multi-agent-workspace")
        self.hub_file = self.root / "docs" / "HUB.md"
        self.comm_dir = self.root / "communication"
        self.reports_dir = self.root / "reports"
        
    def check_agent_activities(self):
        """에이전트 활동 자동 감지"""
        activities = {}
        
        for agent in ['claude', 'gemini', 'codex']:
            agent_dir = self.comm_dir / agent
            if not agent_dir.exists():
                continue
                
            # 최근 파일 확인
            recent_files = []
            for file in agent_dir.glob("*.md"):
                if file.stat().st_mtime > (datetime.now() - timedelta(hours=2)).timestamp():
                    recent_files.append({
                        'name': file.name,
                        'modified': datetime.fromtimestamp(file.stat().st_mtime),
                        'content_preview': self._get_content_preview(file)
                    })
            
            if recent_files:
                activities[agent] = {
                    'status': 'active',
                    'recent_files': recent_files,
                    'last_activity': max(f['modified'] for f in recent_files)
                }
            else:
                activities[agent] = {'status': 'idle', 'recent_files': []}
        
        return activities
    
    def _get_content_preview(self, file_path):
        """파일 내용에서 작업 상태 추출"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 진행 상태 키워드 감지
            if '완료' in content or '✅' in content:
                return 'completed'
            elif '진행' in content or '작업' in content:
                return 'in_progress'  
            elif '할당' in content or '지시' in content:
                return 'assigned'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def update_hub_automatically(self):
        """HUB.md 자동 업데이트"""
        activities = self.check_agent_activities()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 현재 HUB.md 읽기
        if not self.hub_file.exists():
            return False
            
        with open(self.hub_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 자동 업데이트 섹션 생성
        update_section = f"""
## 🤖 자동 상태 업데이트 (마지막 업데이트: {current_time})

### 에이전트 활동 현황
"""
        
        for agent, activity in activities.items():
            if activity['status'] == 'active':
                last_time = activity['last_activity'].strftime("%H:%M")
                update_section += f"- **{agent.upper()}**: 활성 (마지막 활동: {last_time})\n"
                for file_info in activity['recent_files'][:2]:  # 최근 2개만
                    update_section += f"  └─ {file_info['name']} ({file_info['content_preview']})\n"
            else:
                update_section += f"- **{agent.upper()}**: 대기중\n"
        
        # 기존 자동 업데이트 섹션 찾기 및 교체
        if "## 🤖 자동 상태 업데이트" in content:
            # 기존 섹션 교체
            lines = content.split('\n')
            new_lines = []
            skip = False
            
            for line in lines:
                if line.startswith("## 🤖 자동 상태 업데이트"):
                    skip = True
                    new_lines.extend(update_section.strip().split('\n'))
                elif line.startswith("##") and skip:
                    skip = False
                    new_lines.append(line)
                elif not skip:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
        else:
            # 새 섹션 추가 (Active Tasks 뒤에)
            content = content.replace(
                "## Active Tasks",
                f"## Active Tasks{update_section}"
            )
        
        # 파일 저장
        with open(self.hub_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def check_system_metrics(self):
        """시스템 메트릭 자동 수집"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'files_count': len(list(self.root.rglob("*.py"))),
            'recent_commits': self._get_recent_commits(),
            'disk_usage': self._get_disk_usage()
        }
        
        # 메트릭 저장
        metrics_file = self.root / ".agents" / "auto_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def _get_recent_commits(self):
        """최근 커밋 정보"""
        try:
            result = subprocess.run([
                'git', 'log', '--oneline', '-5'
            ], capture_output=True, text=True, cwd=self.root)
            
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n'))
            return 0
        except:
            return 0
    
    def _get_disk_usage(self):
        """디스크 사용량 (MB)"""
        try:
            total_size = 0
            for file in self.root.rglob("*"):
                if file.is_file() and not any(part.startswith('.git') for part in file.parts):
                    total_size += file.stat().st_size
            return round(total_size / (1024 * 1024), 1)
        except:
            return 0
    
    def generate_daily_summary(self):
        """일일 요약 자동 생성"""
        activities = self.check_agent_activities()
        metrics = self.check_system_metrics()
        
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'agent_activities': len([a for a in activities.values() if a['status'] == 'active']),
            'total_files': metrics['files_count'],
            'disk_usage_mb': metrics['disk_usage'],
            'auto_updates': True
        }
        
        # 일일 요약 저장
        summary_file = self.root / "reports" / f"daily_summary_{summary['date']}.json"
        self.reports_dir.mkdir(exist_ok=True)
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 일일 요약 생성: {summary_file.name}")
        return summary
    
    def run_auto_update(self):
        """전체 자동 업데이트 실행"""
        print("🤖 자동 상태 업데이트 시작...")
        
        try:
            # 1. HUB 업데이트
            if self.update_hub_automatically():
                print("✅ HUB.md 자동 업데이트 완료")
            
            # 2. 시스템 메트릭 수집
            metrics = self.check_system_metrics()
            print(f"📊 시스템 메트릭 수집 완료 ({metrics['files_count']}개 파일)")
            
            # 3. 일일 요약 생성
            summary = self.generate_daily_summary()
            print(f"📋 일일 요약 생성 완료 (활성 에이전트: {summary['agent_activities']}개)")
            
            print("🎉 자동 업데이트 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 자동 업데이트 오류: {e}")
            return False

def main():
    updater = AutoStatusUpdater()
    success = updater.run_auto_update()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())