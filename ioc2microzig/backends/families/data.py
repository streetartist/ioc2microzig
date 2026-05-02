"""Portable metadata-only backend."""

from __future__ import annotations

from ...templating import render_template
from ..registry import BACKENDS


def render() -> str:
    return render_template(BACKENDS["data"].template)
