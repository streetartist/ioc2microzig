"""Generic MicroZig hal.pins.GlobalConfiguration context builder."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Sequence

from ...models import IocConfig, PinConfig
from ...templating import render_template
from ...utils import unique_zig_identifiers, zig_string
from ..common import indent_lines, render_peripheral_clock_todos, render_rcc_comments
from ..registry import BACKENDS


def render(cfg: IocConfig, pins: Sequence[PinConfig]) -> str:
    physical = [p for p in pins if not p.is_virtual and p.port is not None and p.number is not None and p.peripheral not in {"SYS", "RCC"}]
    by_port: dict[str, list[PinConfig]] = defaultdict(list)
    aliases = dict(zip([p.index for p in physical], unique_zig_identifiers([p.zig_name_seed for p in physical])))
    for p in physical:
        by_port[p.gpio_port_field].append(p)

    ports: list[dict[str, object]] = []
    for port in sorted(by_port):
        ports.append({
            "name": port,
            "pins": [
                {
                    "field": p.pin_field,
                    "alias": zig_string(aliases[p.index]),
                    "mode": mode_context(p),
                }
                for p in sorted(by_port[port], key=lambda x: x.number or 0)
            ],
        })
    return render_template(
        BACKENDS["pins"].template,
        ports=ports,
        clock_todos=indent_lines(render_peripheral_clock_todos(pins), "    "),
        rcc_comments=indent_lines(render_rcc_comments(cfg), "    "),
        uarts=uart_v3_lines(cfg),
    )


def uart_v3_lines(cfg: IocConfig) -> list[dict[str, str]]:
    uarts: list[dict[str, str]] = []
    for comp in cfg.components:
        name = comp.name.upper()
        if not re.match(r"^(USART|UART)\d+$", name):
            continue
        uarts.append({"instance": name})
    return uarts


def mode_context(p: PinConfig) -> dict[str, str]:
    sig = p.signal.upper()
    mode = p.gpio_mode.upper()
    base = {
        "pull": pull_expr(p.gpio_pull),
        "output_type": "OpenDrain" if "OPEN_DRAIN" in p.gpio_output_type.upper() else "PushPull",
        "speed": speed_expr(p.gpio_speed),
        "alternate": infer_alternate_function(p),
    }

    if sig == "GPIO_OUTPUT" or "OUTPUT" in mode:
        return {"kind": "output", **base}
    if sig == "GPIO_INPUT" or "INPUT" in mode or "EXTI" in sig:
        return {"kind": "input", **base}
    if "ANALOG" in sig or sig.startswith("ADC") or sig.startswith("DAC"):
        return {"kind": "analog", **base}
    if p.peripheral not in {"GPIO", "SYS", "RCC", "UNKNOWN"}:
        return {"kind": "alternate_function", **base}
    return {"kind": "input", **base}


def pull_expr(value: str) -> str:
    v = value.upper()
    if "PULLUP" in v or v.endswith("_UP"):
        return "PullUp"
    if "PULLDOWN" in v or v.endswith("_DOWN"):
        return "PullDown"
    return "Floating"


def speed_expr(value: str) -> str:
    v = value.upper()
    if "VERY_HIGH" in v or "HIGH" in v:
        return "HighSpeed"
    if "MEDIUM" in v:
        return "MediumSpeed"
    return "LowSpeed"


def infer_alternate_function(p: PinConfig) -> str:
    for key, value in p.user_keys.items():
        haystack = f"{key}={value}".upper()
        match = re.search(r"AF(\d+)", haystack)
        if match:
            n = int(match.group(1))
            if 0 <= n <= 15:
                return f"AF{n}"
    return "AF0"
