"""STM32F1 MicroZig HAL board initialization context builder."""

from __future__ import annotations

import re
from typing import Mapping, Sequence

from ...models import IocConfig, PinConfig
from ...templating import render_template
from ...utils import unique_zig_identifiers, zig_identifier
from ..common import indent_lines, render_rcc_comments
from ..registry import BACKENDS


def render(cfg: IocConfig, pins: Sequence[PinConfig]) -> str:
    physical = [p for p in pins if not p.is_virtual and p.port is not None and p.number is not None and p.peripheral not in {"SYS", "RCC"}]
    aliases = unique_zig_identifiers([p.zig_name_seed for p in physical])
    ports = sorted({p.gpio_port_field for p in physical})
    periphs = sorted({peripheral_clock_name(p) for p in physical if peripheral_clock_name(p)})
    for timer_name in timer_components(cfg):
        if timer_name not in periphs:
            periphs.append(timer_name)
    timers, pwm_outputs = timer_runtime(cfg, physical, aliases)
    return render_template(
        BACKENDS["hal"].template,
        pins=[pin_context(alias, p) for alias, p in zip(aliases, physical)],
        gpio_ports=ports,
        enable_afio=any(pin_uses_alternate_function(p) for p in physical),
        peripheral_clocks=periphs,
        rcc=rcc_context(cfg),
        timers=timers,
        pwm_outputs=pwm_outputs,
        uarts=uart_runtime(cfg),
        rcc_comments=indent_lines(render_rcc_comments(cfg), "    "),
    )


def pin_context(alias: str, p: PinConfig) -> dict[str, object]:
    sig = p.signal.upper()
    mode = p.gpio_mode.upper()
    pull = p.gpio_pull.upper()
    setup: dict[str, object]
    if sig == "GPIO_OUTPUT" or "OUTPUT" in mode:
        setup = {
            "kind": "output",
            "mode": "alternate_function_open_drain" if "OPEN_DRAIN" in p.gpio_output_type.upper() else "general_purpose_push_pull",
            "speed": speed_value(p),
        }
    elif sig == "GPIO_INPUT" or "INPUT" in mode:
        if "PULLUP" in pull:
            setup = {"kind": "input", "mode": "pull", "pull": "up"}
        elif "PULLDOWN" in pull:
            setup = {"kind": "input", "mode": "pull", "pull": "down"}
        else:
            setup = {"kind": "input", "mode": "floating", "pull": ""}
    elif pin_uses_alternate_function(p) and not ("RX" in sig or "MISO" in sig):
        mode_name = "alternate_function_open_drain" if "SCL" in sig or "SDA" in sig else "alternate_function_push_pull"
        setup = {"kind": "output", "mode": mode_name, "speed": "max_50MHz"}
    elif "RX" in sig or "MISO" in sig:
        setup = {"kind": "input", "mode": "pull", "pull": "up"}
    else:
        setup = {"kind": "todo"}
    return {
        "alias": alias,
        "port": p.port,
        "number": p.number,
        "name": p.name,
        "signal": p.signal or "GPIO",
        "setup": setup,
    }


def speed_value(p: PinConfig) -> str:
    return "max_50MHz" if "HIGH" in p.gpio_speed.upper() or "50" in p.gpio_speed else "max_10MHz"


def rcc_context(cfg: IocConfig) -> dict[str, object]:
    fields: list[dict[str, str]] = []
    flags: list[dict[str, str]] = []
    mapping = [
        ("SYSCLKSource", "SYSCLKSource"),
        ("PLLSourceVirtual", "PLLSource"),
        ("PLLMUL", "PLLMUL"),
        ("APB1CLKDivider", "APB1CLKDivider"),
        ("APB2CLKDivider", "APB2CLKDivider"),
        ("AHBCLKDivider", "AHBCLKDivider"),
    ]
    for source, target in mapping:
        value = cfg.rcc.get(source, "")
        if value:
            fields.append({"name": target, "value": value})
    pll_src = cfg.rcc.get("PLLSourceVirtual", "")
    if "HSE" in pll_src or any("HSE" in value for value in cfg.rcc.values()):
        flags.append({"name": "HSEOscillator", "value": "true"})
    return {"fields": fields, "flags": flags}


def pin_uses_alternate_function(p: PinConfig) -> bool:
    sig = p.signal.upper()
    mode = p.gpio_mode.upper()
    return (
        "ALTERNATE" in mode
        or bool(re.search(r"(TIM\d+|S_TIM\d+|USART\d+|UART\d+|SPI\d+|I2C\d+)", sig))
        or any(token in sig for token in ("_CH", "_TX", "_RX", "_SCK", "_MOSI", "_MISO", "_SCL", "_SDA"))
    )


def peripheral_clock_name(p: PinConfig) -> str:
    haystack = f"{p.peripheral}_{p.signal}".upper()
    match = re.search(r"(TIM\d+|USART\d+|UART\d+|SPI\d+|I2C\d+|ADC\d+|DAC\d+|CAN\d*)", haystack)
    return match.group(1) if match else ""


def timer_components(cfg: IocConfig) -> list[str]:
    timers: list[str] = []
    for comp in cfg.components:
        if re.match(r"^TIM\d+$", comp.name.upper()):
            timers.append(comp.name.upper())
    return timers


def timer_runtime(cfg: IocConfig, pins: Sequence[PinConfig], aliases: Sequence[str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    timers: list[dict[str, object]] = []
    api: list[dict[str, object]] = []
    timer_aliases: dict[str, str] = {}
    periods: dict[str, str] = {}
    for comp in cfg.components:
        timer = comp.name.upper()
        if not re.match(r"^TIM\d+$", timer):
            continue
        channels = pwm_channels(comp.config)
        if not channels:
            continue
        alias = zig_identifier(f"{timer}_pwm", lower=True)
        timer_aliases[timer] = alias
        prescaler = int_expr(comp.config.get("Prescaler", ""), default="0")
        period = int_expr(comp.config.get("Period", ""), default="65535")
        periods[timer] = period
        timers.append({
            "alias": alias,
            "instance": timer,
            "prescaler": prescaler,
            "period": period,
            "channels": [{"index": channel - 1} for channel in channels],
        })
    for pin, pin_alias in zip(pins, aliases):
        match = re.search(r"(TIM\d+)_CH(\d+)", pin.signal.upper())
        if not match:
            continue
        timer = match.group(1)
        if timer not in timer_aliases:
            continue
        channel = int(match.group(2)) - 1
        if not 0 <= channel <= 3:
            continue
        fn_suffix = zig_identifier(pin_alias, lower=True)
        period_name = zig_identifier(f"{fn_suffix}_period", lower=True)
        api.append({
            "suffix": fn_suffix,
            "period_const": period_name,
            "period": periods.get(timer, "65535"),
            "timer_alias": timer_aliases[timer],
            "channel": channel,
        })
    return timers, api


def uart_runtime(cfg: IocConfig) -> list[dict[str, str]]:
    uarts: list[dict[str, str]] = []
    for comp in cfg.components:
        name = comp.name.upper()
        if not re.match(r"^(USART|UART)\d+$", name):
            continue
        alias = zig_identifier(name, lower=True)
        uarts.append({"alias": alias, "instance": name})
    return uarts


def pwm_channels(config: Mapping[str, str]) -> list[int]:
    channels: list[int] = []
    for key, value in config.items():
        haystack = f"{key} {value}".upper()
        if "PWM" not in haystack:
            continue
        match = re.search(r"TIM_CHANNEL_(\d+)", haystack)
        if match:
            channels.append(int(match.group(1)))
    return sorted(set(ch for ch in channels if 1 <= ch <= 4))


def int_expr(value: str, *, default: str) -> str:
    text = value.strip()
    if not text:
        return default
    if re.fullmatch(r"[0-9xXa-fA-F+\-*/() ]+", text):
        return text
    return default
