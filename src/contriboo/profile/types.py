"""Common type aliases used by profile analysis layer."""

from typing import Literal

type DaysRange = int | Literal["all"]
"""Allowed period argument: positive day count or `"all"` for full history."""
