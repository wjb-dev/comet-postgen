from fastapi import FastAPI
import socket
from haraka.utils import Logger

class PyFast:
    """
    A helper class to handle initialization and shutdown messaging for a FastAPI application.
    """
    def __init__(self, variant: str = "PyFast"):
        """
        Initializes the PyFast instance with a logger.

        Args:
            variant (str): A string identifier for the application. Default is 'PyFast'.
        """
        self.variant = variant
        self.logger = Logger(self.variant).start_logger()

    def init(self, settings, app: FastAPI):
        """
        Initializes the application and logs Swagger UI availability.

        Args:
            settings: A settings object containing application configuration (e.g., port).
            app (FastAPI): The FastAPI application instance.
        """
        try:
            port = settings.port
            docs_path = app.docs_url or "/docs"  # Default to '/docs' if not set
            local_url = f"http://localhost:{port}{docs_path}"

            # Resolve the network-accessible hostname
            host = socket.gethostbyname(socket.gethostname())
            network_url = f"http://{host}:{port}{docs_path}"

            # Log the Swagger UI URLs
            self.logger.info(f"Swagger UI available at: {local_url}")
            self.logger.info(f"Network Swagger UI available at: {network_url}")

        except Exception as e:
            self.logger.warn(f"Failed to determine network URL: {e}")

    def destroy(self):
        """
        Logs a shutdown message when the application is shutting down.
        """
        self.logger.info("🛑 Application is shutting down!")
