#!/usr/bin/env python3
"""
MCP AI Proxy Server
- Claude Code와 다른 AI 모델들(qwen, kimi2, meta)을 연결하는 MCP 서버
- Claude가 필요에 따라 다른 AI 모델들을 도구로 사용할 수 있게 함
"""

import asyncio
import json
import sys
import argparse
from typing import Any, Dict, List, Optional
from pathlib import Path

# MCP 관련 임포트 (실제 환경에 맞게 조정 필요)
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.types import (
        CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult,
        Tool, TextContent, ImageContent, EmbeddedResource
    )
except ImportError:
    print("MCP 라이브러리가 설치되지 않았습니다. pip install mcp를 실행하세요.")
    sys.exit(1)

class AIModelProxy:
    """AI 모델 프록시 베이스 클래스"""
    
    def __init__(self, model_name: str, specialization: str = "general"):
        self.model_name = model_name
        self.specialization = specialization
        
    async def generate_response(self, prompt: str, context: str = None, **kwargs) -> str:
        """AI 모델 응답 생성 (서브클래스에서 구현)"""
        raise NotImplementedError
        
    def get_capabilities(self) -> List[str]:
        """모델의 능력 반환"""
        return ["text_generation"]

class QwenProxy(AIModelProxy):
    """Qwen 모델 프록시"""
    
    def __init__(self):
        super().__init__("qwen/qwen3-32b", "coding")
        
    async def generate_response(self, prompt: str, context: str = None, **kwargs) -> str:
        """Qwen 모델 호출 (실제 API 연동 필요)"""
        # TODO: 실제 Qwen API 호출 구현
        return f"[Qwen Response] {prompt[:100]}... (구현 필요)"
        
    def get_capabilities(self) -> List[str]:
        return ["code_generation", "code_review", "debugging", "refactoring"]

class KimiProxy(AIModelProxy):
    """Kimi 모델 프록시"""
    
    def __init__(self):
        super().__init__("kimi2", "reasoning")
        
    async def generate_response(self, prompt: str, context: str = None, **kwargs) -> str:
        """Kimi 모델 호출 (실제 API 연동 필요)"""
        # TODO: 실제 Kimi API 호출 구현
        return f"[Kimi Deep Analysis] {prompt[:100]}... (구현 필요)"
        
    def get_capabilities(self) -> List[str]:
        return ["deep_reasoning", "analysis", "planning", "complex_problem_solving"]

class MetaLlamaProxy(AIModelProxy):
    """Meta Llama 모델 프록시"""
    
    def __init__(self, variant: str = "3.1-8b"):
        model_name = f"llama-{variant}-instant"
        super().__init__(model_name, "quick_response")
        self.variant = variant
        
    async def generate_response(self, prompt: str, context: str = None, **kwargs) -> str:
        """Llama 모델 호출 (실제 API 연동 필요)"""
        # TODO: 실제 Llama API 호출 구현
        return f"[Llama {self.variant}] {prompt[:100]}... (구현 필요)"
        
    def get_capabilities(self) -> List[str]:
        return ["quick_response", "general_chat", "simple_tasks"]

class MCPAIProxyServer:
    """MCP AI Proxy 서버"""
    
    def __init__(self):
        self.server = Server("ai-model-proxy")
        self.models = {
            "qwen": QwenProxy(),
            "kimi": KimiProxy(), 
            "meta_fast": MetaLlamaProxy("3.1-8b"),
            "meta_large": MetaLlamaProxy("3.3-70b")
        }
        self.setup_tools()
        
    def setup_tools(self):
        """MCP 도구 설정"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """사용 가능한 AI 모델 도구 목록 반환"""
            tools = []
            
            for model_id, model in self.models.items():
                tools.append(Tool(
                    name=f"ai_{model_id}",
                    description=f"{model.model_name} - {model.specialization} 전문",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "AI 모델에 전달할 프롬프트"
                            },
                            "context": {
                                "type": "string", 
                                "description": "추가 컨텍스트 (선택사항)",
                                "default": ""
                            },
                            "max_tokens": {
                                "type": "integer",
                                "description": "최대 토큰 수",
                                "default": 2000
                            },
                            "temperature": {
                                "type": "number",
                                "description": "창의성 수준 (0.0-1.0)",
                                "default": 0.7
                            }
                        },
                        "required": ["prompt"]
                    }
                ))
                
            # 스마트 라우팅 도구
            tools.append(Tool(
                name="ai_smart_route",
                description="작업 유형에 따라 최적의 AI 모델 자동 선택",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "수행할 작업 설명"
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["coding", "analysis", "planning", "quick_answer", "general"],
                            "description": "작업 유형 힌트 (선택사항)"
                        },
                        "context": {
                            "type": "string",
                            "description": "추가 컨텍스트"
                        }
                    },
                    "required": ["task"]
                }
            ))
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """AI 모델 도구 호출 처리"""
            
            if name == "ai_smart_route":
                return await self._handle_smart_route(arguments)
            
            elif name.startswith("ai_"):
                model_id = name[3:]  # "ai_" 제거
                if model_id in self.models:
                    return await self._handle_model_call(model_id, arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"알 수 없는 모델: {model_id}"
                        )],
                        isError=True
                    )
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"알 수 없는 도구: {name}"
                )],
                isError=True
            )
    
    async def _handle_smart_route(self, arguments: Dict[str, Any]) -> CallToolResult:
        """스마트 라우팅 처리"""
        task = arguments.get("task", "")
        task_type = arguments.get("task_type", "")
        context = arguments.get("context", "")
        
        # 작업 유형 자동 감지
        if not task_type:
            task_type = self._detect_task_type(task)
        
        # 최적 모델 선택
        selected_model = self._select_best_model(task_type, task)
        
        # 선택된 모델로 작업 수행
        model_args = {
            "prompt": task,
            "context": context
        }
        
        response = await self._handle_model_call(selected_model, model_args)
        
        # 선택된 모델 정보 추가
        if not response.isError:
            original_text = response.content[0].text
            enhanced_text = f"**[{self.models[selected_model].model_name} 응답]**\n\n{original_text}"
            response.content[0].text = enhanced_text
        
        return response
    
    def _detect_task_type(self, task: str) -> str:
        """작업 유형 자동 감지"""
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ['code', 'function', 'class', 'debug', 'refactor', 'python', 'javascript']):
            return "coding"
        elif any(keyword in task_lower for keyword in ['analyze', 'think', 'complex', 'architecture', 'design']):
            return "analysis"
        elif any(keyword in task_lower for keyword in ['plan', 'strategy', 'roadmap', 'steps']):
            return "planning"
        elif any(keyword in task_lower for keyword in ['quick', 'simple', 'fast', 'brief']):
            return "quick_answer"
        else:
            return "general"
    
    def _select_best_model(self, task_type: str, task: str) -> str:
        """작업 유형에 따른 최적 모델 선택"""
        model_mapping = {
            "coding": "qwen",
            "analysis": "kimi", 
            "planning": "kimi",
            "quick_answer": "meta_fast",
            "general": "meta_large"
        }
        
        return model_mapping.get(task_type, "meta_large")
    
    async def _handle_model_call(self, model_id: str, arguments: Dict[str, Any]) -> CallToolResult:
        """개별 모델 호출 처리"""
        model = self.models[model_id]
        
        try:
            prompt = arguments.get("prompt", "")
            context = arguments.get("context", "")
            max_tokens = arguments.get("max_tokens", 2000)
            temperature = arguments.get("temperature", 0.7)
            
            response = await model.generate_response(
                prompt=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=response
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"모델 호출 오류: {str(e)}"
                )],
                isError=True
            )
    
    async def run(self, transport_type: str = "stdio"):
        """MCP 서버 실행"""
        if transport_type == "stdio":
            # stdio 전송 방식으로 실행
            from mcp.server.stdio import stdio_server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="ai-model-proxy",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities()
                    )
                )

async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="MCP AI Proxy Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio"], 
                       help="전송 방식")
    parser.add_argument("--debug", action="store_true", help="디버그 모드")
    
    args = parser.parse_args()
    
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    server = MCPAIProxyServer()
    await server.run(args.transport)

if __name__ == "__main__":
    asyncio.run(main())