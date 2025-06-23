from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True, slots=True)
class PostGenConfig:
    language: str
    project_slug: str
    author: str
    description: str
    project_dir: Path
    swagger: bool
