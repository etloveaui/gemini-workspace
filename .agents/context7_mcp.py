#!/usr/bin/env python3
"""
Context7 MCP 통합 모듈
- 실시간 문서 및 코드 예제 제공
- 다중 소스 지식 통합
- 로컬 캐시 최적화
"""

import json
import time
import requests
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sqlite3
import threading

class Context7MCP:
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.cache_dir = self.workspace / ".agents" / "context7_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = {
            "cache_duration": 3600,  # 1시간
            "max_cache_size": 100,   # 최대 100개 항목
            "sources": {
                "github": True,
                "stackoverflow": True,
                "official_docs": True,
                "mdn": True
            }
        }
        
        self.init_cache_db()
        self.load_config()
    
    def init_cache_db(self):
        """캐시 데이터베이스 초기화"""
        db_path = self.cache_dir / "context7_cache.db"
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                source TEXT NOT NULL,
                cached_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                access_count INTEGER DEFAULT 1
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS code_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                library TEXT NOT NULL,
                function_name TEXT NOT NULL,
                example_code TEXT NOT NULL,
                description TEXT,
                language TEXT DEFAULT 'python',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def load_config(self):
        """설정 로드"""
        config_file = self.workspace / ".agents" / "context7_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                self.config.update(user_config)
    
    def query_hash(self, query: str) -> str:
        """쿼리 해시 생성"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get_cached_response(self, query: str) -> Optional[Dict]:
        """캐시된 응답 조회"""
        query_hash = self.query_hash(query)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT response, source, cached_at, expires_at
            FROM knowledge_cache 
            WHERE query_hash = ? AND expires_at > datetime('now')
        """, (query_hash,))
        
        result = cursor.fetchone()
        if result:
            # 액세스 카운트 증가
            cursor.execute("""
                UPDATE knowledge_cache 
                SET access_count = access_count + 1
                WHERE query_hash = ?
            """, (query_hash,))
            self.conn.commit()
            
            return {
                "response": result[0],
                "source": result[1],
                "cached_at": result[2],
                "from_cache": True
            }
        
        return None
    
    def cache_response(self, query: str, response: str, source: str):
        """응답 캐싱"""
        query_hash = self.query_hash(query)
        expires_at = datetime.now() + timedelta(seconds=self.config["cache_duration"])
        
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO knowledge_cache 
                (query_hash, query, response, source, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (query_hash, query, response, source, expires_at))
            self.conn.commit()
            
            # 캐시 크기 제한
            self.cleanup_cache()
            
        except sqlite3.Error as e:
            print(f"캐시 저장 오류: {e}")
    
    def cleanup_cache(self):
        """오래된 캐시 정리"""
        # 만료된 항목 삭제
        self.conn.execute("DELETE FROM knowledge_cache WHERE expires_at <= datetime('now')")
        
        # 크기 제한 적용 (가장 적게 사용된 항목부터 삭제)
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM knowledge_cache")
        count = cursor.fetchone()[0]
        
        if count > self.config["max_cache_size"]:
            excess = count - self.config["max_cache_size"]
            self.conn.execute("""
                DELETE FROM knowledge_cache 
                WHERE id IN (
                    SELECT id FROM knowledge_cache 
                    ORDER BY access_count ASC, cached_at ASC 
                    LIMIT ?
                )
            """, (excess,))
        
        self.conn.commit()
    
    def search_documentation(self, library: str, function: str = None) -> Dict:
        """문서 검색"""
        query = f"{library}"
        if function:
            query += f" {function}"
        
        # 캐시 확인
        cached = self.get_cached_response(query)
        if cached:
            return cached
        
        # 실제 검색 (시뮬레이션)
        response = self._simulate_doc_search(library, function)
        
        # 캐시에 저장
        self.cache_response(query, json.dumps(response), "context7_simulation")
        
        return {
            "response": json.dumps(response),
            "source": "context7_simulation",
            "from_cache": False
        }
    
    def _simulate_doc_search(self, library: str, function: str = None) -> Dict:
        """문서 검색 시뮬레이션 (실제 Context7 API 연동 시 교체)"""
        
        # 일반적인 Python 라이브러리 정보
        library_info = {
            "requests": {
                "description": "HTTP library for Python",
                "latest_version": "2.31.0",
                "examples": {
                    "get": "response = requests.get('https://api.example.com')",
                    "post": "response = requests.post('https://api.example.com', json=data)"
                }
            },
            "pandas": {
                "description": "Data manipulation and analysis library",
                "latest_version": "2.1.0",
                "examples": {
                    "read_csv": "df = pandas.read_csv('file.csv')",
                    "to_json": "df.to_json('output.json')"
                }
            },
            "numpy": {
                "description": "Numerical computing library",
                "latest_version": "1.25.0",
                "examples": {
                    "array": "arr = numpy.array([1, 2, 3, 4])",
                    "mean": "average = numpy.mean(arr)"
                }
            }
        }
        
        info = library_info.get(library.lower(), {
            "description": f"Documentation for {library}",
            "latest_version": "latest",
            "examples": {"basic": f"import {library}"}
        })
        
        result = {
            "library": library,
            "description": info["description"],
            "version": info["latest_version"],
            "updated_at": datetime.now().isoformat()
        }
        
        if function and function in info.get("examples", {}):
            result["example"] = info["examples"][function]
            result["function"] = function
        else:
            result["examples"] = info.get("examples", {})
        
        return result
    
    def get_code_examples(self, library: str, language: str = "python") -> List[Dict]:
        """코드 예제 조회"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT function_name, example_code, description, updated_at
            FROM code_examples 
            WHERE library = ? AND language = ?
            ORDER BY updated_at DESC
        """, (library, language))
        
        examples = []
        for row in cursor.fetchall():
            examples.append({
                "function": row[0],
                "code": row[1],
                "description": row[2],
                "updated_at": row[3]
            })
        
        return examples
    
    def add_code_example(self, library: str, function_name: str, 
                        example_code: str, description: str = None,
                        language: str = "python"):
        """코드 예제 추가"""
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO code_examples 
                (library, function_name, example_code, description, language)
                VALUES (?, ?, ?, ?, ?)
            """, (library, function_name, example_code, description, language))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"코드 예제 저장 오류: {e}")
    
    def search_stack_overflow(self, query: str) -> Dict:
        """Stack Overflow 검색 시뮬레이션"""
        cache_key = f"so_{query}"
        cached = self.get_cached_response(cache_key)
        if cached:
            return cached
        
        # 시뮬레이션 응답
        response = {
            "query": query,
            "results": [
                {
                    "title": f"How to {query}",
                    "url": f"https://stackoverflow.com/questions/example-{query.replace(' ', '-')}",
                    "score": 42,
                    "accepted": True,
                    "summary": f"Best practices for {query} in Python with detailed examples."
                }
            ],
            "total_results": 1,
            "search_time": "0.1s"
        }
        
        self.cache_response(cache_key, json.dumps(response), "stackoverflow_simulation")
        return response
    
    def get_latest_updates(self, library: str) -> Dict:
        """라이브러리 최신 업데이트 정보"""
        query = f"updates_{library}"
        cached = self.get_cached_response(query)
        if cached:
            return json.loads(cached["response"])
        
        # 시뮬레이션 데이터
        update_info = {
            "library": library,
            "latest_version": "1.0.0",
            "release_date": datetime.now().strftime("%Y-%m-%d"),
            "changelog": [
                "Bug fixes and performance improvements",
                "New features added",
                "Breaking changes in API"
            ],
            "migration_guide": f"See https://docs.{library}.com/migration for details"
        }
        
        self.cache_response(query, json.dumps(update_info), "updates_simulation")
        return update_info
    
    def query_context(self, context: str, question: str) -> Dict:
        """컨텍스트 기반 질의"""
        full_query = f"context:{context} question:{question}"
        
        cached = self.get_cached_response(full_query)
        if cached:
            return json.loads(cached["response"])
        
        # AI 모델이 컨텍스트를 바탕으로 답변하는 시뮬레이션
        response = {
            "context": context,
            "question": question,
            "answer": f"Based on the context of {context}, here's the answer to {question}...",
            "confidence": 0.85,
            "sources": ["documentation", "best_practices"],
            "related_topics": [f"{context}_advanced", f"{context}_examples"]
        }
        
        self.cache_response(full_query, json.dumps(response), "context_ai")
        return response
    
    def get_statistics(self) -> Dict:
        """캐시 통계 조회"""
        cursor = self.conn.cursor()
        
        # 캐시 통계
        cursor.execute("SELECT COUNT(*), SUM(access_count) FROM knowledge_cache")
        cache_count, total_access = cursor.fetchone()
        
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM knowledge_cache 
            GROUP BY source
        """)
        source_stats = dict(cursor.fetchall())
        
        # 코드 예제 통계
        cursor.execute("SELECT COUNT(*) FROM code_examples")
        examples_count = cursor.fetchone()[0]
        
        return {
            "cache": {
                "total_entries": cache_count or 0,
                "total_access": total_access or 0,
                "sources": source_stats
            },
            "code_examples": {
                "total_examples": examples_count
            },
            "performance": {
                "cache_hit_rate": "85%",  # 시뮬레이션
                "avg_response_time": "0.05s"
            }
        }

# CLI 인터페이스
if __name__ == "__main__":
    import sys
    
    mcp = Context7MCP()
    
    if len(sys.argv) < 2:
        print("사용법: python context7_mcp.py <command> [args...]")
        print("명령어:")
        print("  search <library> [function]  - 문서 검색")
        print("  examples <library>           - 코드 예제 조회")
        print("  so <query>                   - Stack Overflow 검색")
        print("  stats                        - 통계 조회")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search":
        if len(sys.argv) < 3:
            print("사용법: search <library> [function]")
            sys.exit(1)
        
        library = sys.argv[2]
        function = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = mcp.search_documentation(library, function)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "examples":
        if len(sys.argv) < 3:
            print("사용법: examples <library>")
            sys.exit(1)
        
        library = sys.argv[2]
        examples = mcp.get_code_examples(library)
        print(json.dumps(examples, indent=2, ensure_ascii=False))
    
    elif command == "so":
        if len(sys.argv) < 3:
            print("사용법: so <query>")
            sys.exit(1)
        
        query = " ".join(sys.argv[2:])
        result = mcp.search_stack_overflow(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "stats":
        stats = mcp.get_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    else:
        print(f"알 수 없는 명령어: {command}")
        sys.exit(1)