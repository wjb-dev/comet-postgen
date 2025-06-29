from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple
import yaml
from pathspec import PathSpec

_MANIFEST_DIR = Path(__file__).resolve().parent.parent.parent / "utils" / "manifests"

@dataclass(frozen=True, slots=True)
class PostGenConfig:
    variant: str
    project_slug: str
    author_gh: str
    project_dir: Path
    description: str
    use_git: bool
    confirm_remote: bool
    verbose: bool = False
    services: List[str] = None
    evm: bool = False # Extreme Verbosity Mode - For in depth debugging dev tool


def load_manifest(variant: str) -> dict:
    """Return the entire manifest dictionary for the given variant."""
    manifest_path = _MANIFEST_DIR / f"{variant}.yml"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No manifest found for variant '{variant}' "
            f"(expected {manifest_path})"
        )

    doc = yaml.safe_load(manifest_path.read_text())
    if not isinstance(doc, dict):
        raise ValueError(f"Manifest {manifest_path} must be a dictionary")

    if "keep" not in doc:
        raise ValueError(f"Manifest {manifest_path} missing a `keep:` section")

    if "protected" not in doc:
        raise ValueError(f"Manifest {manifest_path} missing a `protected:` section")

    if not isinstance(doc["keep"], Iterable):
        raise TypeError(f"`keep` section in {manifest_path} must be a list")

    if not isinstance(doc["protected"], Iterable):
        raise TypeError(f"`protected` section in {manifest_path} must be a list")

    return doc



def build_spec(patterns: Iterable[str]) -> PathSpec:
    """Compile patterns using git-style wildmatch syntax."""
    return PathSpec.from_lines("gitwildmatch", patterns)