import subprocess, sys
from pathlib import Path
from typing import List, Optional

class CommandRunner:
    """Thin wrapper around subprocess.run with logging & graceful error-handling."""

    def run(
        self,
        cmd: List[str],
        *,
        cwd: Optional[Path] = None,
        check: bool = True,
        label: str = "[post_gen]"
    ) -> Optional[subprocess.CompletedProcess]:
        cmd_str = " ".join(cmd)
        print(f"{label} Running: {cmd_str}")
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
                print(f"{label} stdout:\n{result.stdout.strip()}")
            if result.stderr:
                print(f"{label} stderr:\n{result.stderr.strip()}", file=sys.stderr)
            return result
        except subprocess.CalledProcessError as e:
            print(f"{label} ERROR: command failed ({cmd_str})", file=sys.stderr)
            if e.stdout:
                print(f"{label} stdout:\n{e.stdout.strip()}", file=sys.stderr)
            if e.stderr:
                print(f"{label} stderr:\n{e.stderr.strip()}", file=sys.stderr)
            if check:
                sys.exit(e.returncode)
            return None
        except FileNotFoundError:
            print(f"{label} ERROR: command not found: {cmd[0]}", file=sys.stderr)
            if check:
                sys.exit(1)
            return None
