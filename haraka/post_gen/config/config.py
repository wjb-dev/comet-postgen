from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import yaml
from pathspec import PathSpec

_MANIFEST_DIR = Path(__file__).resolve().parent.parent.parent / "utils" / "manifests"

@dataclass(frozen=True, slots=True)
class PostGenConfig:
    variant: str
    project_slug: str
    author: str
    description: str
    project_dir: Path
    create_repo: bool


def load_manifest(variant: str) -> list[str]:
    """Return the `keep:` pattern list from `<variant>.yml`."""
    manifest_path = _MANIFEST_DIR / f"{variant}.yml"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No manifest found for variant '{variant}' "
            f"(expected {manifest_path})"
        )
    doc = yaml.safe_load(manifest_path.read_text())
    if not isinstance(doc, dict) or "keep" not in doc:
        raise ValueError(f"Manifest {manifest_path} missing a `keep:` section")
    keep_patterns = doc["keep"]
    if not isinstance(keep_patterns, Iterable):
        raise TypeError(f"`keep` section in {manifest_path} must be a list")
    return list(keep_patterns)


def build_spec(patterns: Iterable[str]) -> PathSpec:
    """Compile patterns using git-style wildmatch syntax."""
    return PathSpec.from_lines("gitwildmatch", patterns)