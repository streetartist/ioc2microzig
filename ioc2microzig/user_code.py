"""Preserve CubeMX-style user code regions across regeneration."""

from __future__ import annotations

import re

BEGIN_RE = re.compile(r"^([ \t]*)// USER CODE BEGIN ([A-Za-z0-9_.:-]+)[ \t]*$", re.MULTILINE)
END_RE = re.compile(r"^([ \t]*)// USER CODE END ([A-Za-z0-9_.:-]+)[ \t]*$", re.MULTILINE)


def extract_user_regions(text: str) -> dict[str, str]:
    """Return region name -> body, excluding USER CODE marker lines."""
    regions: dict[str, str] = {}
    pos = 0
    while True:
        begin = BEGIN_RE.search(text, pos)
        if begin is None:
            break
        name = begin.group(2)
        end = END_RE.search(text, begin.end())
        if end is None:
            pos = begin.end()
            continue
        if end.group(2) == name:
            regions[name] = text[begin.end() : end.start()]
            pos = end.end()
        else:
            pos = begin.end()
    return regions


def merge_user_regions(generated: str, previous: str) -> tuple[str, list[str]]:
    """Insert previous USER CODE bodies into matching regions in generated text.

    Returns the merged text and a list of previous region names that no longer
    exist in the generated file.
    """
    old_regions = extract_user_regions(previous)
    if not old_regions:
        return generated, []

    used: set[str] = set()
    out: list[str] = []
    pos = 0
    while True:
        begin = BEGIN_RE.search(generated, pos)
        if begin is None:
            out.append(generated[pos:])
            break
        name = begin.group(2)
        end = END_RE.search(generated, begin.end())
        if end is None:
            out.append(generated[pos:])
            break

        out.append(generated[pos : begin.end()])
        if end.group(2) == name and name in old_regions:
            out.append(old_regions[name])
            used.add(name)
        else:
            out.append(generated[begin.end() : end.start()])
        out.append(generated[end.start() : end.end()])
        pos = end.end()

    missing = sorted(set(old_regions) - used)
    return "".join(out), missing
