"""Shared helpers for backend renderers."""

from __future__ import annotations

from typing import Sequence

from ..models import IocConfig, PinConfig


def render_rcc_comments(cfg: IocConfig) -> str:
    if not cfg.rcc:
        return "// No RCC.* entries found."
    interesting = [
        "OscillatorType", "HSE_VALUE", "LSE_VALUE", "HSI_VALUE", "SYSCLKSource",
        "PLLSourceVirtual", "PLLM", "PLLN", "PLLP", "PLLQ", "PLLR",
        "AHBCLKDivider", "APB1CLKDivider", "APB2CLKDivider",
    ]
    lines = []
    for key in interesting:
        if key in cfg.rcc:
            lines.append(f"// RCC.{key} = {cfg.rcc[key]}")
    for key, value in cfg.rcc.items():
        if key not in interesting and any(token in key.upper() for token in ("PLL", "CLK", "OSC", "HSE", "HSI", "LSE", "LSI")):
            lines.append(f"// RCC.{key} = {value}")
    return "\n".join(lines) if lines else "// RCC entries exist, but none matched the summary filter."


def render_peripheral_clock_todos(pins: Sequence[PinConfig]) -> str:
    periphs = sorted({p.peripheral for p in pins if p.peripheral not in {"GPIO", "SYS", "RCC", "UNKNOWN"}})
    if not periphs:
        return "// No non-GPIO peripheral clocks inferred."
    return "\n".join(f"// TODO: enable/configure clock for {p}." for p in periphs)


def indent_lines(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line else prefix for line in text.splitlines())
