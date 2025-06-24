import subprocess, sys
from pathlib import Path
from typing import List, Optional
from haraka.utils import Logger

class CommandRunner:
    
    """Thin wrapper around subprocess.run with logging & graceful error-handling."""

    def __init__(self, logger: Logger) -> None:
        self._log = logger

    def run(
        self,
        cmd: List[str],
        *,
        cwd: Optional[Path] = None,
        check: bool = True,
    ) -> Optional[subprocess.CompletedProcess]:
        cmd_str = " ".join(cmd)
        self._log.info(f"Running: {cmd_str}")
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.stdout:
                self._log.info(f"stdout:\n{result.stdout.strip()}")
            if result.stderr:
                self._log.warn(f"stderr:\n{result.stderr.strip()}", file=sys.stderr)
            return result
        except subprocess.CalledProcessError as e:
            self._log.error(f"command failed: ({cmd_str})", file=sys.stderr)
            if e.stdout:
                self._log.error(f"stdout:\n{e.stdout.strip()}", file=sys.stderr)
            if e.stderr:
                self._log.error(f"stderr:\n{e.stderr.strip()}", file=sys.stderr)
            if check:
                sys.exit(e.returncode)
            return None
        except FileNotFoundError:
            self._log.error(f"command not found: {cmd[0]}", file=sys.stderr)
            if check:
                sys.exit(1)
            return None
