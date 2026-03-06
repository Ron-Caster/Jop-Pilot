"""
config.settings
~~~~~~~~~~~~~~~~
Loads application configuration from a YAML file and exposes it
as a typed dataclass.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml


@dataclass
class AppConfig:
    """Typed container for every configurable value."""

    # ── Auth ──────────────────────────────────────────────
    email: str = ""
    password: str = ""

    # ── Search ────────────────────────────────────────────
    keywords: List[str] = field(default_factory=list)
    experience: str = ""          # e.g. "3" (years)
    location: str = ""

    # ── Browser ───────────────────────────────────────────
    headless: bool = False
    implicit_wait: int = 10       # seconds


def load_config(path: str | Path | None = None) -> AppConfig:
    """
    Read *config.yaml* and return a populated :class:`AppConfig`.

    Parameters
    ----------
    path : str | Path | None
        Explicit path to the YAML file.  When *None* the loader looks
        for ``config.yaml`` in the project root (same directory as
        ``main.py``).
    """
    if path is None:
        # Resolve relative to the project root
        project_root = Path(__file__).resolve().parent.parent
        path = project_root / "config.yaml"
    else:
        path = Path(path)

    if not path.exists():
        print(f"[config] ⚠  {path} not found – using defaults.")
        return AppConfig()

    with open(path, "r", encoding="utf-8") as fh:
        raw: dict = yaml.safe_load(fh) or {}

    # Flatten nested sections into a single dict
    flat: dict = {}
    for section in ("auth", "search", "browser"):
        if section in raw and isinstance(raw[section], dict):
            flat.update(raw[section])

    return AppConfig(
        email=flat.get("email", ""),
        password=flat.get("password", ""),
        keywords=flat.get("keywords", []),
        experience=str(flat.get("experience", "")),
        location=flat.get("location", ""),
        headless=flat.get("headless", False),
        implicit_wait=int(flat.get("implicit_wait", 10)),
    )
