#!/usr/bin/env python3
"""
JSON-RPC 2.0 over TCP 서버 베이스 클래스

사용법:
    class MyBridge(BaseBridge):
        def __init__(self):
            super().__init__(port=8765)
            self.register_method("my_method", self.handle_my_method)

        def handle_my_method(self, params):
            return {"result": "ok"}

    if __name__ == "__main__":
        bridge = MyBridge()
        bridge.run()
"""
import asyncio
import json
import os
import signal
import sys
from abc import ABC
from typing import Any, Callable, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JsonRpcError(Exception):
    """JSON-RPC 에러"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class BaseBridge(ABC):
    """JSON-RPC 2.0 서버 베이스 클래스"""

    def __init__(self, port: int):
        self.port = port
        self._methods: Dict[str, Callable] = {}
        self._server: Optional[asyncio.AbstractServer] = None
        self._shutdown_event = asyncio.Event()

        # 기본 메서드 등록
        self.register_method("ping", self._handle_ping)
        self.register_method("shutdown", self._handle_shutdown)

    def register_method(self, name: str, handler: Callable) -> None:
        """RPC 메서드 등록"""
        self._methods[name] = handler
        logger.info(f"Registered method: {name}")

    def _handle_ping(self, params: Dict) -> Dict:
        """핑/퐁 헬스체크"""
        return {"pong": True, "methods": list(self._methods.keys())}

    def _handle_shutdown(self, params: Dict) -> Dict:
        """서버 종료"""
        self._shutdown_event.set()
        return {"shutting_down": True}

    async def _handle_request(self, data: bytes) -> bytes:
        """단일 JSON-RPC 요청 처리"""
        try:
            request = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            return self._error_response(None, -32700, f"Parse error: {e}")

        # JSON-RPC 2.0 검증
        if request.get("jsonrpc") != "2.0":
            return self._error_response(request.get("id"), -32600, "Invalid Request: jsonrpc must be '2.0'")

        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if not method:
            return self._error_response(req_id, -32600, "Invalid Request: method required")

        if method not in self._methods:
            return self._error_response(req_id, -32601, f"Method not found: {method}")

        try:
            # 동기/비동기 핸들러 지원
            handler = self._methods[method]
            if asyncio.iscoroutinefunction(handler):
                result = await handler(params)
            else:
                result = handler(params)

            return self._success_response(req_id, result)

        except JsonRpcError as e:
            return self._error_response(req_id, e.code, e.message, e.data)
        except Exception as e:
            logger.exception(f"Error handling method {method}")
            return self._error_response(req_id, -32603, f"Internal error: {str(e)}")

    def _success_response(self, req_id: Any, result: Any) -> bytes:
        """성공 응답 생성"""
        response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        }
        return (json.dumps(response, ensure_ascii=False) + "\n").encode('utf-8')

    def _error_response(self, req_id: Any, code: int, message: str, data: Any = None) -> bytes:
        """에러 응답 생성"""
        response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        if data is not None:
            response["error"]["data"] = data
        return (json.dumps(response, ensure_ascii=False) + "\n").encode('utf-8')

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """클라이언트 연결 처리"""
        peer = writer.get_extra_info('peername') or 'unknown'
        logger.info(f"Client connected: {peer}")

        try:
            while not self._shutdown_event.is_set():
                try:
                    # NDJSON: 줄바꿈으로 구분된 JSON
                    line = await asyncio.wait_for(reader.readline(), timeout=300)
                    if not line:
                        break

                    response = await self._handle_request(line.strip())
                    writer.write(response)
                    await writer.drain()

                except asyncio.TimeoutError:
                    # 5분 타임아웃: 연결 유지, 로그만
                    continue

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Client error: {e}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
            logger.info(f"Client disconnected: {peer}")

    async def _run_server(self):
        """서버 실행"""
        self._server = await asyncio.start_server(
            self._handle_client,
            host='127.0.0.1',
            port=self.port
        )

        logger.info(f"Server started on 127.0.0.1:{self.port}")

        async with self._server:
            await self._shutdown_event.wait()

        logger.info("Server shutting down...")

    def _setup_signals(self):
        """시그널 핸들러 설정"""
        try:
            loop = asyncio.get_event_loop()

            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(self._handle_signal(s))
                )
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            logger.info("Signal handlers not supported on this platform")

    async def _handle_signal(self, sig: signal.Signals):
        """시그널 처리"""
        logger.info(f"Received signal {sig.name}")
        self._shutdown_event.set()

    def run(self):
        """서버 시작 (blocking)"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            self._setup_signals()
            loop.run_until_complete(self._run_server())

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            logger.info("Server stopped")
