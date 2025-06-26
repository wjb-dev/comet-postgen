from __future__ import annotations
import sys
from typing import TextIO


class Logger:
    def __init__(self, label: str = "", verbose: bool = False, evm: bool = True) -> None:
        self.label = label
        self.verbose = verbose
        self.evm = evm # Extreme Verbosity Mode (In-depth debug logs)

    def start_logger(self, verbose) -> Logger:
        label = Logger.get_label(self.label)
        return Logger(label, verbose)

    def info(self, msg: str) -> None:
        print(f"{self.label} INFO: {msg}")

    def debug(self, msg: str) -> None:
        if self.verbose:
            print(f"🔴  DEBUG: {msg}")

    def warn(self, msg: str, file: TextIO = sys.stderr) -> None:
        print(f"{self.label} WARNING: {msg}", file=file)

    def error(self, msg: str, file: TextIO = sys.stderr) -> None:
        print(f"{self.label} ERROR: {msg}", file=file)

    @staticmethod
    def get_label(variant: str) -> str:
        if variant == "go":
            return f"[🔥Go Fast: post_gen]"
        return f"[🔥post_gen ({variant})]"

