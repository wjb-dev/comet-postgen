import asyncio
import socket
from enum import Enum, auto
from fastapi import FastAPI
from haraka.utils import Logger


class LifecycleState(Enum):
    UNINITIALIZED = auto()
    STARTED = auto()
    DESTROYED = auto()


class Lifecycle:
    """
    A helper class to handle initialization and shutdown messaging for a FastAPI application.
    Also supports registration of app-specific background tasks (e.g., Kafka consumers).
    """
    def __init__(self, variant: str = "PyFast"):
        self.variant = variant
        self.logger = Logger(self.variant).start_logger()
        self.state = LifecycleState.UNINITIALIZED
        self.background_tasks = []
        self._running_tasks = []

    def register_startup_task(self, coro_fn):
        """Register an async function to be run during startup."""
        self.background_tasks.append(coro_fn)

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
        except Exception as e:
            self.logger.warn(f"⚠️ Failed to determine network URL: {e}")

        # Launch registered background tasks
        for coro_fn in self.background_tasks:
            task = asyncio.create_task(self._wrap_task(coro_fn))
            self._running_tasks.append(task)

        self.state = LifecycleState.STARTED

    async def _wrap_task(self, coro_fn):
        try:
            await coro_fn()
        except asyncio.CancelledError:
            self.logger.info(f"🛑 Task {coro_fn.__name__} cancelled.")
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Task {coro_fn.__name__} failed:")
            traceback.print_exc()

    async def destroy(self):
        if self.state == LifecycleState.DESTROYED:
            self.logger.warn("🟡 destroy() called, but app is already shut down.")
            return

        self.logger.info("🛑 Application is shutting down!")

        # Cancel all running background tasks
        for task in self._running_tasks:
            task.cancel()
        await asyncio.gather(*self._running_tasks, return_exceptions=True)

        self.state = LifecycleState.DESTROYED
