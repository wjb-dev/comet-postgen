from __future__ import annotations
import sys
from typing import TextIO, Optional


class Logger:
    def __init__(self, label: str = "", verbose: bool = False, evm: bool = True) -> None:
        self.label = label
        self.verbose = verbose
        self.evm = evm

    def start_logger(self, verbose: bool = False) -> Logger:
        label = Logger.get_label(self.label)
        return Logger(label, verbose)

    def info(self, msg: str, extra: Optional[dict] = None) -> None:
        print(f"{self.label} INFO: {msg}{self._format_extra(extra)}")

    def debug(self, msg: str, extra: Optional[dict] = None) -> None:
        if self.verbose:
            print(f"{self.label} 🔴 DEBUG: {msg}{self._format_extra(extra)}")

    def warn(self, msg: str, file: TextIO = sys.stderr, extra: Optional[dict] = None) -> None:
        print(f"{self.label} ⚠️ WARNING: {msg}{self._format_extra(extra)}", file=file)

    def error(self, msg: str, file: TextIO = sys.stderr, extra: Optional[dict] = None) -> None:
        print(f"{self.label} ❌ ERROR: {msg}{self._format_extra(extra)}", file=file)

    @staticmethod
    def get_label(variant: str) -> str:
        if variant == "go":
            return f"[🔥Go Fast: post_gen]"
        if variant == "PyFast":
            return f"[🐍 PyFast]:"
        return f"[🔥post_gen ({variant})]"

    @staticmethod
    def _format_extra(extra: Optional[dict]) -> str:
        if not extra:
            return ""
        formatted = " | " + " ".join(f"{k}={v}" for k, v in extra.items())
        return formatted
