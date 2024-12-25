from enum import Enum
from typing import Optional, Tuple, Any
from asyncio import Lock
import logging

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

class SessionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ACTIVE = "active"
    ERROR = "error"

class MCPSession:
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        self.state = SessionState.DISCONNECTED
        self.session: Optional[ClientSession] = None
        self._streams: Optional[Tuple[Any, Any]] = None
        self._lock = Lock()
        self._client_context = None

    async def establish_session(self) -> None:
        """Establishes a new session."""
        print(31)
        if self.state == SessionState.CONNECTING:
            return
            
        print(32)
        async with self._lock:
            try:
                print(33)
                self.state = SessionState.CONNECTING
                print(34)
                self._client_context = stdio_client(self.server_params)
                print(35)
                self._streams = await self._client_context.__aenter__()
                print(36)
                self.session = ClientSession(*self._streams)
                print(self.session)
                print(37)
                await self.session.initialize()
                await self.session.initialize()
                print(38)
                self.state = SessionState.ACTIVE
            except Exception as e:
                self.state = SessionState.ERROR
                logger.error(f"Failed to establish session: {e}")
                await self.cleanup()
                raise

    async def ensure_session(self) -> ClientSession:
        """Ensures an active session exists and returns it."""
        print(21)
        if self.state == SessionState.ACTIVE and self.session is not None:
            return self.session

        print(22)
        if self.state in (SessionState.ERROR, SessionState.DISCONNECTED):
            await self.establish_session()
        
        print(23)
        if self.session is None:
            raise RuntimeError("Failed to establish session")
            
        return self.session

    async def cleanup(self) -> None:
        """Cleans up session resources."""
        if self.session is not None:
            try:
                await self.session.aclose()
            except:
                pass
            self.session = None

        if self._client_context is not None:
            try:
                await self._client_context.__aexit__(None, None, None)
            except:
                pass
            self._client_context = None

        self._streams = None
        self.state = SessionState.DISCONNECTED