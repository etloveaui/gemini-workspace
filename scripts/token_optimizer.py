#!/usr/bin/env python3
"""
토큰 효율성 최적화 시스템
- 컨텍스트 압축
- 스마트 캐싱
- 중복 작업 제거
- 토큰 사용량 50% 절감 목표
"""
import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class TokenOptimizer:
    """토큰 사용량 최적화 시스템"""
    
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.cache_db = self.root / ".agents" / "token_cache.db"
        self.stats_file = self.root / ".agents" / "token_stats.json"
        
        self.cache_db.parent.mkdir(exist_ok=True, parents=True)
        self._init_database()
    
    def _init_database(self):
        """캐시 데이터베이스 초기화"""
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context_hash TEXT UNIQUE NOT NULL,
                    compressed_context TEXT NOT NULL,
                    original_size INTEGER NOT NULL,
                    compressed_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    last_used TEXT NOT NULL,
                    use_count INTEGER DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS response_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_hash TEXT UNIQUE NOT NULL,
                    response TEXT NOT NULL,
                    tokens_saved INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)
    
    def compress_context(self, context: str, max_length: int = 2000) -> str:
        """컨텍스트 압축 (핵심 정보만 추출)"""
        
        # 해시 생성
        context_hash = hashlib.md5(context.encode()).hexdigest()
        
        # 캐시 확인
        cached = self._get_cached_context(context_hash)
        if cached:
            return cached
        
        # 압축 로직
        compressed = self._compress_text(context, max_length)
        
        # 캐시 저장
        self._save_compressed_context(context_hash, context, compressed)
        
        return compressed
    
    def _compress_text(self, text: str, max_length: int) -> str:
        """텍스트 압축 알고리즘"""
        if len(text) <= max_length:
            return text
        
        # 1. 중요 섹션 추출
        important_sections = []
        
        # 오류 메시지 (최우선)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['error', 'fail', 'exception', '❌', '🚨']):
                # 오류 라인 + 전후 2줄씩
                start = max(0, i-2)
                end = min(len(lines), i+3)
                important_sections.extend(lines[start:end])
        
        # 2. 코드 블록 압축
        code_blocks = []
        in_code = False
        current_block = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code:
                    # 코드 블록 끝
                    if len('\n'.join(current_block)) < 500:  # 짧은 코드만 유지
                        code_blocks.extend(current_block)
                    else:
                        # 긴 코드는 요약
                        code_blocks.append(f"[코드 블록: {len(current_block)}줄 생략]")
                    current_block = []
                in_code = not in_code
            elif in_code:
                current_block.append(line)
            else:
                # 일반 텍스트에서 중요한 부분
                if any(keyword in line.lower() for keyword in 
                       ['todo', '작업', '완료', '진행', '상태', 'status', 'priority']):
                    important_sections.append(line)
        
        # 3. 최종 압축 텍스트 생성
        compressed_parts = []
        
        # 중요 섹션 추가
        if important_sections:
            compressed_parts.append("🎯 핵심 내용:")
            compressed_parts.extend(important_sections[:10])  # 최대 10줄
        
        # 코드 블록 추가
        if code_blocks:
            compressed_parts.append("\n💻 코드:")
            compressed_parts.extend(code_blocks[:5])  # 최대 5개 블록
        
        # 길이 조정
        result = '\n'.join(compressed_parts)
        if len(result) > max_length:
            result = result[:max_length] + "\n[...더 많은 내용 생략...]"
        
        return result
    
    def cache_response(self, request: str, response: str, ttl_hours: int = 24) -> bool:
        """응답 캐싱"""
        request_hash = hashlib.md5(request.encode()).hexdigest()
        expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
        
        tokens_saved = len(response) // 4  # 대략적인 토큰 수
        
        try:
            with sqlite3.connect(self.cache_db) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO response_cache 
                    (request_hash, response, tokens_saved, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (request_hash, response, tokens_saved, datetime.now().isoformat(), expires_at))
            return True
        except Exception as e:
            print(f"ERROR: response cache failed - {e}")
            return False
    
    def get_cached_response(self, request: str) -> Optional[str]:
        """캐시된 응답 조회"""
        request_hash = hashlib.md5(request.encode()).hexdigest()
        
        try:
            with sqlite3.connect(self.cache_db) as conn:
                cursor = conn.execute("""
                    SELECT response, expires_at FROM response_cache 
                    WHERE request_hash = ? AND expires_at > ?
                """, (request_hash, datetime.now().isoformat()))
                
                result = cursor.fetchone()
                if result:
                    self._update_token_stats("cache_hit", len(result[0]) // 4)
                    return result[0]
        except Exception:
            pass
        
        return None
    
    def remove_duplicates(self, file_path: str) -> int:
        """파일에서 중복 내용 제거"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            unique_lines = []
            seen_lines = set()
            
            for line in lines:
                # 공백 제거 후 비교
                clean_line = line.strip()
                if clean_line and clean_line not in seen_lines:
                    unique_lines.append(line)
                    seen_lines.add(clean_line)
                elif not clean_line:  # 빈 줄은 유지 (하나만)
                    if not unique_lines or unique_lines[-1].strip():
                        unique_lines.append(line)
            
            # 파일 업데이트
            new_content = '\n'.join(unique_lines)
            if len(new_content) < len(content):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                saved_chars = len(content) - len(new_content)
                self._update_token_stats("deduplication", saved_chars // 4)
                return saved_chars
        
        except Exception as e:
            print(f"ERROR: dedup failed ({file_path}) - {e}")
        
        return 0
    
    def optimize_communication_files(self) -> Dict[str, int]:
        """통신 파일들 최적화"""
        results = {"files_processed": 0, "tokens_saved": 0}
        
        comm_dir = self.root / "communication"
        if not comm_dir.exists():
            return results
        
        for agent_dir in comm_dir.iterdir():
            if agent_dir.is_dir():
                for file_path in agent_dir.glob("*.md"):
                    # 3일 이상 된 파일만 최적화
                    if (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days >= 3:
                        saved = self.remove_duplicates(str(file_path))
                        if saved > 0:
                            results["files_processed"] += 1
                            results["tokens_saved"] += saved // 4
        
        return results
    
    def get_optimization_stats(self) -> Dict:
        """최적화 통계 반환"""
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
        except:
            stats = {
                "total_tokens_saved": 0,
                "cache_hits": 0,
                "deduplications": 0,
                "compressions": 0,
                "last_updated": datetime.now().isoformat()
            }
        
        # 데이터베이스에서 추가 통계
        try:
            with sqlite3.connect(self.cache_db) as conn:
                # 캐시 통계
                cursor = conn.execute("SELECT COUNT(*), SUM(tokens_saved) FROM response_cache")
                cache_count, cache_tokens = cursor.fetchone()
                
                # 압축 통계  
                cursor = conn.execute("SELECT COUNT(*), SUM(original_size - compressed_size) FROM context_cache")
                compress_count, compress_saved = cursor.fetchone()
                
                stats.update({
                    "active_cache_entries": cache_count or 0,
                    "tokens_saved_by_cache": cache_tokens or 0,
                    "compression_entries": compress_count or 0,
                    "bytes_saved_by_compression": compress_saved or 0
                })
        except:
            pass
        
        return stats
    
    def _get_cached_context(self, context_hash: str) -> Optional[str]:
        """캐시된 컨텍스트 조회"""
        try:
            with sqlite3.connect(self.cache_db) as conn:
                cursor = conn.execute("""
                    SELECT compressed_context FROM context_cache 
                    WHERE context_hash = ?
                """, (context_hash,))
                
                result = cursor.fetchone()
                if result:
                    # 사용 횟수 업데이트
                    conn.execute("""
                        UPDATE context_cache 
                        SET last_used = ?, use_count = use_count + 1
                        WHERE context_hash = ?
                    """, (datetime.now().isoformat(), context_hash))
                    
                    return result[0]
        except:
            pass
        
        return None
    
    def _save_compressed_context(self, context_hash: str, original: str, compressed: str):
        """압축된 컨텍스트 저장"""
        try:
            with sqlite3.connect(self.cache_db) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO context_cache 
                    (context_hash, compressed_context, original_size, compressed_size, created_at, last_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    context_hash, compressed, len(original), len(compressed),
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
        except Exception as e:
            print(f"ERROR: context cache failed - {e}")
    
    def _update_token_stats(self, operation: str, tokens_saved: int):
        """토큰 통계 업데이트"""
        try:
            try:
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
            except:
                stats = {"total_tokens_saved": 0}
            
            stats["total_tokens_saved"] = stats.get("total_tokens_saved", 0) + tokens_saved
            stats[operation] = stats.get(operation, 0) + 1
            stats["last_updated"] = datetime.now().isoformat()
            
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except:
            pass

# 편의 함수들
def optimize_text(text: str, max_length: int = 2000) -> str:
    """텍스트 빠른 최적화"""
    optimizer = TokenOptimizer("C:/Users/etlov/multi-agent-workspace")
    return optimizer.compress_context(text, max_length)

def cleanup_communication_folder() -> Dict[str, int]:
    """통신 폴더 빠른 정리"""
    optimizer = TokenOptimizer("C:/Users/etlov/multi-agent-workspace")
    return optimizer.optimize_communication_files()

if __name__ == "__main__":
    from cli_style import header, section, kv, item
    optimizer = TokenOptimizer("C:/Users/etlov/multi-agent-workspace")

    print(header("Token Optimizer"))

    # 통신 폴더 최적화
    results = optimizer.optimize_communication_files()
    print(item(1, f"Communication optimize - files={results['files_processed']}, tokens_saved={results['tokens_saved']}"))

    # 통계 출력
    stats = optimizer.get_optimization_stats()
    print(item(2, kv("Total Tokens Saved", stats.get('total_tokens_saved', 0))))
    print(item(3, kv("Active Cache Entries", stats.get('active_cache_entries', 0))))

    # 테스트 압축
    test_text = "이것은 테스트 텍스트입니다. " * 100
    compressed = optimizer.compress_context(test_text, 200)
    print(item(4, f"Compress test - original={len(test_text)} compressed={len(compressed)}"))
