"""
Helpers that deal with Unicode column widths and simple emoji detection.
"""
import logging
from wcwidth import wcwidth as _wcwidth

logger = logging.getLogger(__name__)


class WidthUtil:
    """Static helpers – no state required."""

    @staticmethod
    def wcwidth_narrow(ch: str) -> int:
        """
        Return wcwidth’s value for *ch* (0, 1, or 2).
        Keeping the wrapper separate makes unit-testing easier.
        """
        return _wcwidth(ch)

    @classmethod
    def is_emoji_line(cls, text: str) -> bool:
        """
        True if any code-point in *text* takes two columns (typical for emoji).
        """
        for ch in text:
            if cls.wcwidth_narrow(ch) > 1:
                logger.info("%r → is emoji", text)
                return True
        return False
