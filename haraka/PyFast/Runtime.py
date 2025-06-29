import asyncio
import socket
from enum import Enum, auto
from typing import Awaitable, Callable

from fastapi import FastAPI

from haraka.PyFast.core.interfaces import Service
from haraka.utils import Logger

class LifecycleState(Enum):
    UNINITIALIZED = auto()
    STARTED = auto()
    DESTROYED = auto()


class Orchestrator:
    """
    A runtime orchestration manager for FastAPI microservices.

    Supports:
    - Startup/shutdown lifecycle tasks
    - Declarative service readiness tracking
    - Structured logging and Swagger UI auto-announcement
    - Plug-and-play service registration via `.use(service)`
    """
    def __init__(self, variant: str = "PyFast"):
        self.variant = variant
        self.logger = Logger(self.variant).start_logger()
        self.state = LifecycleState.UNINITIALIZED

        self.startup_tasks: list[Callable[[], Awaitable]] = []
        self.shutdown_tasks: list[Callable[[], Awaitable]] = []
        self._running_tasks: list[asyncio.Task] = []

        self._services: list[Service] = []
        self._service_events: dict[str, asyncio.Event] = {}

    def register_startup_task(self, coro_fn: Callable[[], Awaitable]):
        self.startup_tasks.append(coro_fn)

    def register_shutdown_task(self, coro_fn: Callable[[], Awaitable]):
        self.shutdown_tasks.append(coro_fn)

    def register_service(self, name: str):
        if name not in self._service_events:
            self._service_events[name] = asyncio.Event()
            self.logger.debug(f"🛎️ Registered service: {name}")
        else:
            self.logger.warn(f"⚠️ Service '{name}' already registered")

    def mark_ready(self, name: str):
        event = self._service_events.get(name)
        if event and not event.is_set():
            event.set()
            self.logger.info(f"✅ Service '{name}' is ready.")
        elif event:
            self.logger.debug(f"🔁 Service '{name}' was already marked ready.")
        else:
            self.logger.warn(f"⚠️ Tried to mark unknown service '{name}' as ready")

    async def wait_for_all_ready(self, timeout: float = 30.0):
        try:
            await asyncio.wait_for(
                asyncio.gather(*(evt.wait() for evt in self._service_events.values())),
                timeout=timeout
            )
            self.logger.info("✅ All declared services are up and running!")
        except asyncio.TimeoutError:
            unready = [name for name, evt in self._service_events.items() if not evt.is_set()]
            self.logger.error("❌ Timed out waiting for services", extra={"unready_services": unready})
            raise

    def use(self, service: Service):
        service.runtime = self
        self._services.append(service)
        self.register_service(service.name)

    async def start(self, settings, app: FastAPI):
        if self.state != LifecycleState.UNINITIALIZED:
            self.logger.warn(f"🟡 Already started or shut down: {self.state.name}")
            return

        for svc in self._services:
            try:
                await svc.startup()
            except Exception as e:
                self.logger.error(f"❌ Failed to start {svc.name}", extra={"error": str(e)})
                if not getattr(svc, "fail_silently", lambda: False)():
                    raise

        for task_fn in self.startup_tasks:
            task = asyncio.create_task(self._wrap_task(task_fn))
            self._running_tasks.append(task)

        self._print_docs_url(settings, app)
        self.state = LifecycleState.STARTED

    async def destroy(self):
        if self.state == LifecycleState.DESTROYED:
            self.logger.warn("🟡 Already destroyed")
            return

        self.logger.info("🛑 Application is shutting down!")

        for task in self._running_tasks:
            task.cancel()
        await asyncio.gather(*self._running_tasks, return_exceptions=True)

        for svc in reversed(self._services):
            try:
                await svc.shutdown()
            except Exception as e:
                self.logger.error(f"❌ Shutdown failed for {svc.name}", extra={"error": str(e)})

        for task_fn in self.shutdown_tasks:
            try:
                await task_fn()
            except Exception:
                import traceback
                self.logger.error("❌ Shutdown task failed:")
                traceback.print_exc()

        self.state = LifecycleState.DESTROYED

    async def _wrap_task(self, coro_fn: Callable[[], Awaitable]):
        try:
            await coro_fn()
        except asyncio.CancelledError:
            self.logger.info(f"🛑 Task {coro_fn.__name__} cancelled.")
        except Exception:
            import traceback
            self.logger.error(f"❌ Task {coro_fn.__name__} failed:")
            traceback.print_exc()

    def _print_docs_url(self, settings, app: FastAPI):
        try:
            port = settings.port
            docs_path = app.docs_url or "/docs"
            local = f"http://localhost:{port}{docs_path}"
            host = socket.gethostbyname(socket.gethostname())
            net = f"http://{host}:{port}{docs_path}"
            self.logger.info(f"✅ Swagger UI available at: {local}")
            self.logger.info(f"🌐 Network Swagger UI available at: {net}")
        except Exception as e:
            self.logger.warn(f"⚠️ Failed to determine docs URL: {e}")
