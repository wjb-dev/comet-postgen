# tests/test_manifest_equivalence.py
from pathlib import Path

import yaml

_MANIFEST_DIR: Path = Path(__file__).parents[1] / "comet-postgen" / "haraka" / "utils" / "manifests"

def load_via_open(full_path: Path):
    with full_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        raw_patterns = config.get("keep", [])
        keep_patterns = [p.rstrip("/") for p in raw_patterns]
        return keep_patterns

def load_via_manifest_dir(variant: str):
    manifest_path = _MANIFEST_DIR / f"{variant}.yml"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No manifest found for variant '{variant}' (expected {manifest_path})"
        )
    doc = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    raw_patterns = doc["keep"]
    raw_patterns = list(raw_patterns)
    keep_patterns = [p.rstrip("/") for p in raw_patterns]
    return list(keep_patterns)

def test_same_yaml_object():
    variant = "JavaFein"
    full_path = Path(
        "/Users/will/Projects/comet-postgen/haraka/utils/manifests"
    ) / f"{variant}.yml"

    cfg_open  = load_via_open(full_path)
    cfg_read  = load_via_manifest_dir(variant)

    # Structural equality: order in mappings is irrelevant
    assert cfg_open == cfg_read
