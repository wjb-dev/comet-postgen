#!/usr/bin/env python3
"""
haraka.post_gen.utils.purge

Delete all template artefacts that are **not** required for the chosen
variant, as defined by a YAML manifest in `haraka/manifests/<variant>.yml`.

Manifest format (git-wildmatch globs):

    variant: python-fastapi
    keep:
      - src/app/**
      - tests/**
      - Dockerfile
      - chart/**

Anything matching a `keep:` pattern survives. Everything else is removed.

Requires:  pip install pathspec PyYAML
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml
from pathspec import PathSpec

from .files import FileOps
from haraka.utils import Logger, divider
from ..config import config

_MANIFEST_DIR = Path(__file__).resolve().parent.parent.parent / "manifests"


# --------------------------------------------------------------------------- #
# main purger                                                                 #
# --------------------------------------------------------------------------- #
class ResourcePurger:
    """Filesystem cleaner driven by variant manifest files."""

    def __init__(self, fops: FileOps, logger: Logger | None = None) -> None:
        self._f = fops
        self._log = logger or Logger("ResourcePurger")

    # ------------------------------ public API ----------------------------- #
    def purge(self, variant: str, project_dir: Path) -> None:
        """
        Remove everything outside the manifest’s `keep:` patterns.

        Parameters
        ----------
        variant
            Variant key, e.g. ``python-fastapi`` or ``go-grpc-protoc``.
        project_dir
            Root of the freshly generated Cookiecutter project.
        """
        variant = variant.lower()
        self._log.info(f"Starting purge for variant: {variant}")

        keep_patterns = config.load_manifest(variant)
        spec = config.build_spec(keep_patterns)

        self._log.info(f"Keeping {len(keep_patterns)} pattern(s)")

        self._purge_unrelated(project_dir, spec)

        divider("Project tree after purge…")
        self._f.print_tree(project_dir)

    # ----------------------------- internals ------------------------------ #
    def _purge_unrelated(self, root: Path, spec: PathSpec) -> None:
        """
        Walk the project tree; delete every path NOT matched by *spec*.
        """
        for path in root.rglob("*"):
            rel = path.relative_to(root).as_posix()

            if spec.match_file(rel):
                continue  # keep it

            if path.is_dir():
                self._f.remove_dir(path)
            else:
                self._f.remove_file(path)
