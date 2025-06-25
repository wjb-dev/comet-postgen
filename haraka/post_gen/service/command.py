import subprocess, sys
from pathlib import Path
from typing import List, Optional
from haraka.utils import Logger

class CommandRunner:
    
    """Thin wrapper around subprocess.run with logging & graceful error-handling."""

    def __init__(self, logger: Logger) -> None:
        self._log = logger
        self._log.debug("CommandRunner initialized with logger")

    def run(
        self,
        cmd: List[str],
        *,
        cwd: Optional[Path] = None,
        check: bool = True,
    ) -> Optional[subprocess.CompletedProcess]:
        cmd_str = " ".join(cmd)
        self._log.debug(f"Command to be run: {cmd_str}")
        self._log.info(f"Running: {cmd_str}")
        try:
            self._log.debug(f"Executing command with subprocess: {cmd_str}, cwd={cwd}, check={check}")
            result = subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self._log.debug(f"Command execution completed with return code: {result.returncode}")
            if result.stdout:

                self._log.debug("Processing command stdout")
                self._log.info(f"stdout:\n{result.stdout.strip()}")

            self._log.debug("Checking for command stderr")
            if result.stderr:
                self._log.warn(f"stderr:\n{result.stderr.strip()}", file=sys.stderr)
            return result
        except subprocess.CalledProcessError as e:
            self._log.error(f"Command execution raised CalledProcessError: ({cmd_str})", file=sys.stderr)
            self._log.debug(f"Return code: {e.returncode}, stdout: {e.stdout}, stderr: {e.stderr}")
            if e.stdout:
                self._log.error(f"stdout:\n{e.stdout.strip()}", file=sys.stderr)
            if e.stderr:
                self._log.error(f"stderr:\n{e.stderr.strip()}", file=sys.stderr)
            if check:
                sys.exit(e.returncode)
            return None
        except FileNotFoundError:
            self._log.error(f"Command not found: {cmd[0]}", file=sys.stderr)
            self._log.debug(f"Ensure that the command '{cmd[0]}' is installed and available in PATH")
            if check:
                sys.exit(1)
            return None
