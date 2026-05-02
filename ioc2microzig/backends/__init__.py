"""Backend package for family-specific MicroZig init generation."""

from .registry import (
    BACKEND_ALIASES,
    BACKENDS,
    CLI_BACKEND_CHOICES,
    InitBackend,
    normalize_backend_name,
    select_auto_backend,
)

__all__ = [
    "BACKEND_ALIASES",
    "BACKENDS",
    "CLI_BACKEND_CHOICES",
    "InitBackend",
    "normalize_backend_name",
    "select_auto_backend",
]
