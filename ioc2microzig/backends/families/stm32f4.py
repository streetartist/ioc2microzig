"""STM32F4 register-level board initialization context builder."""

from __future__ import annotations

import re
from typing import Sequence

from ...models import IocConfig, PinConfig
from ...templating import render_template
from ...utils import unique_zig_identifiers
from ..common import indent_lines, render_rcc_comments
from ..registry import BACKENDS


def render(cfg: IocConfig, pins: Sequence[PinConfig]) -> str:
    physical = [p for p in pins if not p.is_virtual and p.port is not None and p.number is not None and p.peripheral not in {"SYS", "RCC"}]
    aliases = unique_zig_identifiers([p.zig_name_seed for p in physical])
    return render_template(
        BACKENDS["registers"].template,
        pins=[pin_context(alias, p) for alias, p in zip(aliases, physical)],
        rcc_comments=indent_lines(render_rcc_comments(cfg), "    "),
    )


def pin_context(alias: str, p: PinConfig) -> dict[str, object]:
    sig = p.signal.upper()
    mode = p.gpio_mode.upper()
    if sig == "GPIO_OUTPUT" or "OUTPUT" in mode:
        setup = {"kind": "mode", "mode": "output"}
    elif sig == "GPIO_INPUT" or "INPUT" in mode:
        setup = {"kind": "mode", "mode": "input"}
    elif pin_uses_alternate_function(p):
        setup = {"kind": "alternate", "mode": "alternate", "alternate": infer_alternate_function(p)}
    elif "ANALOG" in sig or "ADC" in sig or "DAC" in sig:
        setup = {"kind": "mode", "mode": "analog"}
    else:
        setup = {"kind": "todo"}
    return {
        "alias": alias,
        "port": f"GPIO{p.port}",
        "number": p.number or 0,
        "name": p.name,
        "signal": p.signal or "GPIO",
        "setup": setup,
    }


def pin_uses_alternate_function(p: PinConfig) -> bool:
    sig = p.signal.upper()
    mode = p.gpio_mode.upper()
    return (
        "ALTERNATE" in mode
        or bool(re.search(r"(TIM\d+|USART\d+|UART\d+|SPI\d+|I2C\d+|CAN\d+|SDIO|USB|ETH)", sig))
        or any(token in sig for token in ("_CH", "_TX", "_RX", "_SCK", "_MOSI", "_MISO", "_SCL", "_SDA"))
    )


def infer_alternate_function(p: PinConfig) -> str:
    for key, value in p.user_keys.items():
        haystack = f"{key}={value}".upper()
        match = re.search(r"AF(\d+)", haystack)
        if match:
            n = int(match.group(1))
            if 0 <= n <= 15:
                return str(n)
    return "0"
