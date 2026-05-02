"""Shared normalization and Zig identifier helpers."""

from __future__ import annotations

import re
from typing import Optional, Sequence

from .constants import *
from .models import IocConfig

def infer_family(mcu_name: str) -> str:
    match = re.match(r"^(STM32[A-Z][0-9])", mcu_name.upper())
    return match.group(1) if match else ""


def classify_signal(signal: str) -> str:
    if not signal:
        return "GPIO"
    s = signal.strip().upper()

    if s.startswith("GPIO_") or s in {"GPIO", "GPXTI", "EVENTOUT"}:
        return "GPIO"
    if s.startswith("SYS_"):
        return "SYS"
    if s.startswith("RCC_"):
        return "RCC"

    for prefix in sorted(SIGNAL_PREFIXES_WITHOUT_INSTANCE, key=len, reverse=True):
        if s == prefix or s.startswith(prefix + "_"):
            return prefix

    for prefix in sorted(SIGNAL_INSTANCE_PREFIXES, key=len, reverse=True):
        match = re.match(rf"^({re.escape(prefix)}\d+[A-Z]?)(?:_|$)", s)
        if match:
            return match.group(1)

    match = PERIPHERAL_NUMBERED_RE.match(s)
    if match:
        return match.group(1)

    head = s.split("_", 1)[0]
    return head or "UNKNOWN"


def normalize_chip_name(cubemx_name: str, cpn: str = "") -> str:
    """Best-effort conversion from CubeMX part names to MicroZig chip constants."""
    name = (cpn or cubemx_name or "").strip().upper()
    if not name:
        return "STM32_CHIP_TODO"
    # Drop package/temperature markers usually present in CubeMX names.
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"[^A-Z0-9]", "", name)
    name = re.sub(r"(TX|RX|VX|YX|ZX|UX|IX|KX)$", "", name)
    name = re.sub(r"T[0-9A-Z]$", "", name)
    if not name.startswith("STM32"):
        return "STM32_CHIP_TODO"
    return name


def default_target_expr(cfg: IocConfig) -> str:
    return f"stm32.chips.{normalize_chip_name(cfg.mcu_name, cfg.mcu_cpn)}"


def parse_include(value: str) -> set[str]:
    parts = [p.strip().lower() for p in value.split(",") if p.strip()]
    if not parts:
        return {"all"}
    aliases = {
        "uart": ["usart", "uart", "lpuart"],
        "serial": ["usart", "uart", "lpuart"],
        "usart": ["usart"],
        "i2c": ["i2c"],
        "i2s": ["i2s"],
        "spi": ["spi"],
        "tim": ["tim", "lptim"],
        "timer": ["tim", "lptim"],
        "adc": ["adc"],
        "dac": ["dac"],
        "gpio": ["gpio"],
        "usb": ["usb", "usb_otg_fs", "usb_otg_hs"],
        "can": ["can", "fdcan"],
        "ethernet": ["eth"],
        "eth": ["eth"],
    }
    result: set[str] = set()
    for part in parts:
        if part == "all":
            result.add("all")
        elif part in aliases:
            result.update(aliases[part])
        else:
            result.add(part)
    return result


def zig_identifier(value: str, *, lower: bool = False) -> str:
    value = value.strip()
    value = re.sub(r"[^0-9A-Za-z_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        value = "unnamed"
    if lower:
        value = camel_or_label_to_snake(value).lower()
    if value[0].isdigit():
        value = "_" + value
    if value in RESERVED_ZIG:
        value += "_"
    return value


def unique_zig_identifiers(seeds: Sequence[str]) -> list[str]:
    used: dict[str, int] = {}
    names: list[str] = []
    for seed in seeds:
        base = zig_identifier(seed, lower=True)
        count = used.get(base, 0)
        used[base] = count + 1
        if count:
            names.append(f"{base}_{count + 1}")
        else:
            names.append(base)
    return names


def camel_or_label_to_snake(value: str) -> str:
    value = value.replace("-", "_").replace(" ", "_")
    # Keep hardware-style acronyms compact: I2C1 -> i2c1, USB_OTG_FS -> usb_otg_fs.
    if not re.search(r"[a-z]", value):
        return re.sub(r"_+", "_", value)
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z])([A-Z])", r"\1_\2", value)
    value = re.sub(r"_+", "_", value)
    return value


def zig_string(value: object) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def zig_bool(value: bool) -> str:
    return "true" if value else "false"


def zig_optional_int(value: Optional[int]) -> str:
    return "null" if value is None else str(value)


def zig_optional_port(value: Optional[str]) -> str:
    return "null" if value is None else f"'{value}'"


def zig_optional_pin(value: Optional[int]) -> str:
    return "null" if value is None else str(value)


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on", "enable", "enabled"}


def parse_int(value: str) -> Optional[int]:
    try:
        return int(str(value).strip(), 0)
    except (TypeError, ValueError):
        return None


def unique_preserving_order(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out

