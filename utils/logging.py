"""
구조적 로깅 및 트레이싱 유틸리티.

기능
- JSON 형태의 구조적 로깅 포맷터
- correlation_id(ContextVar) 기반의 요청 단위 추적
- @trace 데코레이터로 함수 입/출력, 소요시간 로깅

사용 예시
  from utils.logging import init_logging, with_correlation, trace, get_logger
  init_logging(level="INFO")
  with with_correlation():
      @trace
      def work(x: int) -> int:
          return x * 2
      work(21)
"""
from __future__ import annotations

import json
import logging
import os
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional


correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        payload: Dict[str, Any] = {
            "ts": _now_iso(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        cid = correlation_id_var.get()
        if cid:
            payload["correlation_id"] = cid

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        # record.extra dict 지원
        # logging.LoggerAdapter 사용 또는 logger.bind(extra=...) 패턴 대체
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            payload.update(_jsonify(extra))

        return json.dumps(payload, ensure_ascii=False)


def _jsonify(obj: Any) -> Any:
    try:
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, dict):
            return {str(k): _jsonify(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [_jsonify(v) for v in obj]
        if is_dataclass(obj):
            return _jsonify(asdict(obj))
        if hasattr(obj, "__dict__"):
            return _jsonify(obj.__dict__)
        return str(obj)
    except Exception:
        return str(obj)


def init_logging(level: str = "INFO", to_file: Optional[str] = None) -> logging.Logger:
    """루트 로거를 JSON 포맷으로 초기화.

    level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL"
    to_file: 파일 경로 지정 시 파일 핸들러 추가
    """
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    fmt = JsonFormatter()

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)

    if to_file:
        os.makedirs(os.path.dirname(to_file), exist_ok=True)
        fh = logging.FileHandler(to_file, encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)

    return root


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)


def new_correlation_id() -> str:
    return uuid.uuid4().hex


def set_correlation_id(value: Optional[str]) -> None:
    correlation_id_var.set(value)


def get_correlation_id() -> Optional[str]:
    return correlation_id_var.get()


@contextmanager
def with_correlation(cid: Optional[str] = None):
    token = correlation_id_var.set(cid or new_correlation_id())
    try:
        yield correlation_id_var.get()
    finally:
        correlation_id_var.reset(token)


def trace(func: Callable[..., Any]) -> Callable[..., Any]:
    """함수 입/출력과 소요시간을 로깅하는 데코레이터."""

    logger = get_logger(func.__module__)

    def _shorten(value: Any, limit: int = 200) -> Any:
        try:
            s = json.dumps(_jsonify(value), ensure_ascii=False)
        except Exception:
            s = str(value)
        return s if len(s) <= limit else s[: limit - 3] + "..."

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        cid = get_correlation_id() or new_correlation_id()
        set_correlation_id(cid)
        start = time.perf_counter()
        logger.debug(
            "enter",
            extra={
                "extra": {
                    "func": func.__qualname__,
                    "args": _shorten(args),
                    "kwargs": _shorten(kwargs),
                }
            },
        )
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.debug(
                "exit",
                extra={
                    "extra": {
                        "func": func.__qualname__,
                        "elapsed_ms": round(elapsed_ms, 3),
                        "result": _shorten(result),
                    }
                },
            )
            return result
        except Exception as e:  # noqa: BLE001
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "error",
                extra={
                    "extra": {
                        "func": func.__qualname__,
                        "elapsed_ms": round(elapsed_ms, 3),
                    }
                },
                exc_info=True,
            )
            raise e

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__qualname__ = func.__qualname__
    return wrapper

