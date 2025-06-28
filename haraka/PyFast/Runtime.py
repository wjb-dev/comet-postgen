from enum import Enum, auto
from fastapi import FastAPI
import socket
from haraka.utils import Logger


class LifecycleState(Enum):
    UNINITIALIZED = auto()
    STARTED = auto()
    DESTROYED = auto()


class Lifecycle:
    """
    A helper class to handle initialization and shutdown messaging for a FastAPI application.
    Tracks internal state to guard against invalid transitions.
    """
    def __init__(self, variant: str = "PyFast"):
        self.variant = variant
        self.logger = Logger(self.variant).start_logger()
        self.state = LifecycleState.UNINITIALIZED

    async def start(self, settings, app: FastAPI):
        if self.state != LifecycleState.UNINITIALIZED:
            self.logger.warn(f"🟡 Attempted to start, but state is already {self.state.name}")
            return

        try:
            port = settings.port
            docs_path = app.docs_url or "/docs"
            local_url = f"http://localhost:{port}{docs_path}"

            host = socket.gethostbyname(socket.gethostname())
            network_url = f"http://{host}:{port}{docs_path}"

            self.logger.info(f"✅ Swagger UI available at: {local_url}")
            self.logger.info(f"🌐 Network Swagger UI available at: {network_url}")
            self.state = LifecycleState.STARTED

        except Exception as e:
            self.logger.warn(f"⚠️ Failed to determine network URL: {e}")

    async def destroy(self):
        if self.state == LifecycleState.DESTROYED:
            self.logger.warn("🟡 destroy() called, but app is already shut down.")
            return

        self.logger.info("🛑 Application is shutting down!")
        self.state = LifecycleState.DESTROYED
