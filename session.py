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

    async def establish_session(self) -> None:
        """Establishes a new session."""
        if self.state == SessionState.CONNECTING:
            return
            
        async with self._lock:
            try:
                self.state = SessionState.CONNECTING
                self._streams = await stdio_client(self.server_params).__aenter__()
                self.session = ClientSession(*self._streams)
                await self.session.initialize()
                self.state = SessionState.ACTIVE
            except Exception as e:
                self.state = SessionState.ERROR
                logger.error(f"Failed to establish session: {e}")
                await self.cleanup()
                raise

    async def ensure_session(self) -> ClientSession:
        """Ensures an active session exists and returns it."""
        if self.state == SessionState.ACTIVE and self.session is not None:
            return self.session

        if self.state in (SessionState.ERROR, SessionState.DISCONNECTED):
            await self.establish_session()
            
        if self.session is None:
            raise RuntimeError("Failed to establish session")
            
        return self.session

    async def cleanup(self) -> None:
        """Cleans up session resources."""
        if self._streams:
            try:
                await self._streams[0].aclose()
                await self._streams[1].aclose()
            except:
                pass
        self._streams = None
        self.session = None
        self.state = SessionState.DISCONNECTED