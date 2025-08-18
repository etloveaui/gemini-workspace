#!/usr/bin/env python3
"""
스마트 Scratchpad 관리 시스템
- 사용자 요구사항 자동 분류 및 정리
- AI별 자료 자동 분배
- 중요 자료 보존 및 검색
- 임시 파일 자동 정리
"""

import json
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class SmartScratchpad:
    def __init__(self, workspace_path=None):
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent
        else:
            self.workspace_path = Path(workspace_path)
        
        self.scratchpad_path = self.workspace_path / "scratchpad"
        self.config_file = self.workspace_path / ".claude" / "scratchpad_config.json"
        self.index_file = self.scratchpad_path / "_index.json"
        
        # 기본 설정
        self.default_config = {
            "auto_organize": True,
            "archive_after_days": 30,
            "max_temp_files": 50,
            "ai_routing": {
                "claude": ["architecture", "complex", "design", "security"],
                "codex": ["code", "implementation", "test", "debug"],
                "gemini": ["document", "analysis", "status", "log"]
            },
            "file_patterns": {
                "important": ["plan", "spec", "requirement", "design"],
                "temporary": ["temp", "tmp", "test", "debug"],
                "ai_specific": {
                    "claude": ["claude", "cl_", "for_claude"],
                    "codex": ["codex", "cd_", "for_codex"],
                    "gemini": ["gemini", "gm_", "for_gemini"]
                }
            }
        }
        
        self.ensure_structure()
        self.load_config()
    
    def ensure_structure(self):
        """Scratchpad 디렉토리 구조 생성"""
        directories = [
            "incoming",      # 새로 들어온 파일들
            "archive",       # 보관된 파일들
            "ai_tasks",      # AI별 작업 파일들
            "ai_tasks/claude",
            "ai_tasks/codex", 
            "ai_tasks/gemini",
            "important",     # 중요 문서들
            "temp"          # 임시 파일들
        ]
        
        for dir_name in directories:
            (self.scratchpad_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        """설정 로드"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = {**self.default_config, **json.load(f)}
        else:
            self.config = self.default_config.copy()
            self.save_config()
    
    def save_config(self):
        """설정 저장"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def analyze_file_content(self, file_path: Path) -> Dict:
        """파일 내용 분석하여 분류 정보 추출"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # UTF-8이 아닌 파일 처리
            try:
                with open(file_path, 'r', encoding='cp949') as f:
                    content = f.read()
            except:
                return {"category": "binary", "ai_target": None, "importance": "unknown"}
        
        analysis = {
            "category": self.categorize_content(content),
            "ai_target": self.determine_ai_target(content, file_path.name),
            "importance": self.assess_importance(content, file_path.name),
            "keywords": self.extract_keywords(content),
            "size": len(content),
            "lines": content.count('\n') + 1
        }
        
        return analysis
    
    def categorize_content(self, content: str) -> str:
        """콘텐츠 내용 기반 카테고리 분류"""
        content_lower = content.lower()
        
        # 코드 파일 감지
        code_patterns = [
            r'def\s+\w+\(', r'function\s+\w+\(', r'class\s+\w+',
            r'import\s+\w+', r'from\s+\w+\s+import', r'#include',
            r'console\.log', r'print\(', r'System\.out\.println'
        ]
        if any(re.search(pattern, content) for pattern in code_patterns):
            return "code"
        
        # 설계/계획 문서
        if any(word in content_lower for word in ['architecture', 'design', 'plan', 'specification', 'requirement']):
            return "design"
        
        # 분석/보고서
        if any(word in content_lower for word in ['analysis', 'report', 'findings', 'conclusion', 'summary']):
            return "analysis"
        
        # 로그/상태
        if any(word in content_lower for word in ['log', 'status', 'error', 'debug', 'trace']):
            return "log"
        
        # 문서
        if any(word in content_lower for word in ['documentation', 'readme', 'guide', 'manual', 'help']):
            return "documentation"
        
        return "general"
    
    def determine_ai_target(self, content: str, filename: str) -> Optional[str]:
        """AI 타겟 결정"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # 파일명 기반 라우팅
        for ai, patterns in self.config["file_patterns"]["ai_specific"].items():
            if any(pattern in filename_lower for pattern in patterns):
                return ai
        
        # 내용 기반 라우팅
        for ai, keywords in self.config["ai_routing"].items():
            if any(keyword in content_lower for keyword in keywords):
                return ai
        
        # 복잡도 기반 라우팅
        if len(content) > 5000 or content.count('\n') > 100:
            return "claude"  # 복잡한 내용은 Claude에게
        elif "code" in content_lower or "function" in content_lower:
            return "codex"   # 코드 관련은 Codex에게
        elif "status" in content_lower or "log" in content_lower:
            return "gemini"  # 상태/로그는 Gemini에게
        
        return None
    
    def assess_importance(self, content: str, filename: str) -> str:
        """중요도 평가"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # 파일명 기반 중요도
        if any(pattern in filename_lower for pattern in self.config["file_patterns"]["important"]):
            return "high"
        
        if any(pattern in filename_lower for pattern in self.config["file_patterns"]["temporary"]):
            return "low"
        
        # 내용 기반 중요도
        high_importance_keywords = [
            "requirement", "specification", "architecture", "critical", 
            "important", "urgent", "deadline", "milestone"
        ]
        
        if any(keyword in content_lower for keyword in high_importance_keywords):
            return "high"
        
        # 크기 기반 중요도
        if len(content) > 10000:
            return "medium"
        elif len(content) < 500:
            return "low"
        
        return "medium"
    
    def extract_keywords(self, content: str) -> List[str]:
        """키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용 가능)
        words = re.findall(r'\b[a-zA-Z가-힣]{3,}\b', content.lower())
        
        # 불용어 제거
        stopwords = set(['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 
                        'can', 'her', 'was', 'one', 'our', 'had', 'but', 'what'])
        
        # 빈도 계산
        word_freq = {}
        for word in words:
            if word not in stopwords and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 상위 10개 키워드 반환
        return sorted(word_freq.keys(), key=word_freq.get, reverse=True)[:10]
    
    def organize_file(self, file_path: Path) -> Dict:
        """파일 자동 정리"""
        if not file_path.exists():
            return {"status": "error", "message": "File not found"}
        
        # 파일 분석
        analysis = self.analyze_file_content(file_path)
        
        # 목적지 결정
        destination = self.determine_destination(file_path, analysis)
        
        # 파일 이동
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            if destination.exists():
                # 중복 파일 처리
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = destination.name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    new_name = f"{destination.name}_{timestamp}"
                destination = destination.parent / new_name
            
            shutil.move(str(file_path), str(destination))
            
            # 인덱스 업데이트
            self.update_index(destination, analysis)
            
            return {
                "status": "success",
                "original": str(file_path),
                "destination": str(destination),
                "analysis": analysis
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def determine_destination(self, file_path: Path, analysis: Dict) -> Path:
        """파일 목적지 결정"""
        base_name = file_path.name
        
        # 중요도별 처리
        if analysis["importance"] == "high":
            return self.scratchpad_path / "important" / base_name
        
        # AI 타겟별 처리
        if analysis["ai_target"]:
            return self.scratchpad_path / "ai_tasks" / analysis["ai_target"] / base_name
        
        # 카테고리별 처리
        if analysis["category"] == "log":
            return self.scratchpad_path / "archive" / "logs" / base_name
        elif analysis["importance"] == "low":
            return self.scratchpad_path / "temp" / base_name
        else:
            return self.scratchpad_path / "archive" / base_name
    
    def update_index(self, file_path: Path, analysis: Dict):
        """파일 인덱스 업데이트"""
        # 기존 인덱스 로드
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {"files": {}, "last_updated": None}
        
        # 파일 정보 추가
        relative_path = file_path.relative_to(self.scratchpad_path)
        index["files"][str(relative_path)] = {
            **analysis,
            "added_date": datetime.now().isoformat(),
            "file_size": file_path.stat().st_size if file_path.exists() else 0
        }
        
        index["last_updated"] = datetime.now().isoformat()
        
        # 인덱스 저장
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def search_files(self, query: str) -> List[Dict]:
        """파일 검색"""
        if not self.index_file.exists():
            return []
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        results = []
        query_lower = query.lower()
        
        for file_path, info in index["files"].items():
            # 파일명 검색
            if query_lower in file_path.lower():
                results.append({"path": file_path, "info": info, "match_type": "filename"})
                continue
            
            # 키워드 검색
            if any(query_lower in keyword for keyword in info.get("keywords", [])):
                results.append({"path": file_path, "info": info, "match_type": "keyword"})
                continue
            
            # 카테고리 검색
            if query_lower in info.get("category", "").lower():
                results.append({"path": file_path, "info": info, "match_type": "category"})
        
        return results
    
    def cleanup_temp_files(self):
        """임시 파일 정리"""
        temp_dir = self.scratchpad_path / "temp"
        if not temp_dir.exists():
            return
        
        # 오래된 임시 파일 삭제
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = 0
        
        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_date < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
        
        return deleted_count
    
    def generate_ai_assignment_report(self) -> str:
        """AI별 할당된 작업 보고서 생성"""
        if not self.index_file.exists():
            return "인덱스 파일이 없습니다."
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        ai_stats = {"claude": [], "codex": [], "gemini": [], "unassigned": []}
        
        for file_path, info in index["files"].items():
            ai_target = info.get("ai_target", "unassigned")
            if ai_target in ai_stats:
                ai_stats[ai_target].append(file_path)
            else:
                ai_stats["unassigned"].append(file_path)
        
        report = f"""# 🤖 AI 작업 분배 현황

**생성 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 분배 통계
"""
        
        for ai, files in ai_stats.items():
            emoji = {"claude": "🧠", "codex": "⚡", "gemini": "📖", "unassigned": "❓"}[ai]
            report += f"- {emoji} **{ai.title()}**: {len(files)}개 파일\n"
        
        report += "\n## 📋 상세 내역\n\n"
        
        for ai, files in ai_stats.items():
            if files:
                emoji = {"claude": "🧠", "codex": "⚡", "gemini": "📖", "unassigned": "❓"}[ai]
                report += f"### {emoji} {ai.title()}\n"
                for file_path in files[:10]:  # 최대 10개만 표시
                    report += f"- `{file_path}`\n"
                if len(files) > 10:
                    report += f"- ... 외 {len(files) - 10}개 파일\n"
                report += "\n"
        
        return report

# CLI 실행을 위한 메인 함수
if __name__ == "__main__":
    import sys
    
    scratchpad = SmartScratchpad()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "organize":
            if len(sys.argv) > 2:
                file_path = Path(sys.argv[2])
                result = scratchpad.organize_file(file_path)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("사용법: python smart_scratchpad.py organize <file_path>")
        
        elif command == "search":
            if len(sys.argv) > 2:
                query = sys.argv[2]
                results = scratchpad.search_files(query)
                print(f"검색 결과: {len(results)}개")
                for result in results[:10]:
                    print(f"- {result['path']} ({result['match_type']})")
            else:
                print("사용법: python smart_scratchpad.py search <query>")
        
        elif command == "cleanup":
            deleted = scratchpad.cleanup_temp_files()
            print(f"🧹 {deleted}개의 임시 파일을 정리했습니다.")
        
        elif command == "report":
            report = scratchpad.generate_ai_assignment_report()
            print(report)
        
        else:
            print("사용법: python smart_scratchpad.py [organize|search|cleanup|report]")
    else:
        # 기본: 상태 출력
        if scratchpad.index_file.exists():
            with open(scratchpad.index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            file_count = len(index.get("files", {}))
            print(f"📁 Scratchpad: {file_count}개 파일 관리 중")
        else:
            print("📁 Scratchpad: 초기화 필요")