"""STM32CubeMX .ioc parser."""

from __future__ import annotations

import re
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Mapping, Optional, Sequence

from .constants import *
from .models import ComponentConfig, DmaRequestConfig, IocConfig, NvicConfig, PinConfig, RawEntry
from .utils import infer_family, parse_bool, parse_int, unique_preserving_order

def parse_ioc(path: Path) -> IocConfig:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    raw: "OrderedDict[str, str]" = OrderedDict()
    entries: list[RawEntry] = []

    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        match = KEY_VALUE_RE.match(stripped)
        if not match:
            continue
        key, value = match.group(1).strip(), match.group(2).strip()
        raw[key] = value
        entries.append(RawEntry(key=key, value=value, line=line_no))

    pins = extract_pins(raw)
    ip_names = extract_ip_names(raw)
    rcc = scoped(raw, "RCC")
    nvic, nvic_raw = extract_nvic(raw)
    dma, dma_raw = extract_dma(raw)
    components = extract_components(raw, ip_names, pins)

    mcu_name = raw.get("Mcu.Name") or raw.get("Mcu.CPN") or raw.get("Mcu.Device") or ""
    mcu_cpn = raw.get("Mcu.CPN", "")
    return IocConfig(
        path=path,
        raw=raw,
        entries=entries,
        project_name=raw.get("ProjectManager.ProjectName") or path.stem,
        mcu_name=mcu_name,
        mcu_cpn=mcu_cpn,
        mcu_family=raw.get("Mcu.Family") or infer_family(mcu_name),
        package=raw.get("Mcu.Package", ""),
        ip_names=ip_names,
        pins=pins,
        components=components,
        rcc=dict(sorted(rcc.items())),
        nvic=nvic,
        nvic_raw=nvic_raw,
        dma=dma,
        dma_raw=dma_raw,
    )


def scoped(raw: Mapping[str, str], prefix: str) -> dict[str, str]:
    head = prefix + "."
    return {key[len(head):]: value for key, value in raw.items() if key.startswith(head)}


def extract_ip_names(raw: Mapping[str, str]) -> list[str]:
    values: list[tuple[int, str]] = []
    for key, value in raw.items():
        match = re.match(r"^Mcu\.IP(\d+)$", key)
        if match and value:
            values.append((int(match.group(1)), value.strip()))
    values.sort(key=lambda item: item[0])
    names = [value for _, value in values]
    return unique_preserving_order(names)


def split_csvish(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,;]", value or "") if part.strip()]


def first_existing(fields: Mapping[str, str], names: Sequence[str]) -> str:
    for name in names:
        value = fields.get(name, "")
        if value != "":
            return value
    return ""


def first_key_with_prefix(fields: Mapping[str, str], prefixes: Sequence[str]) -> str:
    for prefix in prefixes:
        for key in sorted(fields):
            if key.startswith(prefix) and fields[key] != "":
                return fields[key]
    return ""


def parse_pin_key(prefix: str) -> Optional[tuple[str, bool, Optional[str], Optional[int]]]:
    if VIRTUAL_PIN_RE.match(prefix):
        return prefix, True, None, None
    match = PHYSICAL_PIN_RE.match(prefix)
    if match:
        port, number = match.group(1), int(match.group(2))
        return f"P{port}{number}", False, port, number
    return None


def extract_pins(raw: Mapping[str, str]) -> list[PinConfig]:
    by_pin: "OrderedDict[str, dict[str, str]]" = OrderedDict()
    for key, value in raw.items():
        if "." not in key:
            continue
        prefix, suffix = key.split(".", 1)
        if parse_pin_key(prefix):
            by_pin.setdefault(prefix, {})[suffix] = value

    pins: list[PinConfig] = []
    for ioc_key in sorted(by_pin, key=pin_sort_key):
        fields = by_pin[ioc_key]
        parsed = parse_pin_key(ioc_key)
        if parsed is None:
            continue
        name, is_virtual, port, number = parsed
        label = first_existing(fields, ["GPIO_Label", "GPIO_Label.Signal", "UserLabel", "Label"])
        gpio_mode = first_existing(fields, ["GPIO_Mode", "Mode"]) or first_key_with_prefix(fields, ["GPIO_ModeDefault", "GPIO_Mode"])
        gpio_pull = first_existing(fields, ["GPIO_PuPd", "GPIO_Pull", "GPIO_PullUpPullDown"])
        gpio_speed = first_existing(fields, ["GPIO_Speed", "GPIO_SpeedFrequency", "GPIO_Speed_FREQ"])
        gpio_output_type = first_existing(fields, ["GPIO_OType", "GPIO_OutputType"])
        gpio_output_level = first_existing(fields, ["GPIO_OutputLevel", "GPIO_InitLevel", "PinState"])
        pins.append(PinConfig(
            index=len(pins),
            ioc_key=ioc_key,
            name=name,
            is_virtual=is_virtual,
            port=port,
            number=number,
            signal=fields.get("Signal", ""),
            label=label,
            gpio_mode=gpio_mode,
            gpio_pull=gpio_pull,
            gpio_speed=gpio_speed,
            gpio_output_type=gpio_output_type,
            gpio_output_level=gpio_output_level,
            locked=parse_bool(fields.get("Locked", "false")),
            user_keys=dict(sorted(fields.items())),
        ))
    return pins


def pin_sort_key(pin_key: str) -> tuple[int, str, int, str]:
    parsed = parse_pin_key(pin_key)
    if parsed is None:
        return 2, pin_key, 0, pin_key
    name, is_virtual, port, number = parsed
    if is_virtual:
        return 1, pin_key, 0, pin_key
    return 0, port or "", number or 0, pin_key


def extract_components(raw: Mapping[str, str], ip_names: Sequence[str], pins: Sequence[PinConfig]) -> list[ComponentConfig]:
    component_names: list[str] = []
    component_names.extend(ip_names)

    for key in raw:
        if "." not in key:
            continue
        prefix, _ = key.split(".", 1)
        if parse_pin_key(prefix):
            continue
        if prefix in META_PREFIXES and prefix not in SPECIAL_COMPONENT_PREFIXES:
            continue
        if prefix in SPECIAL_COMPONENT_PREFIXES or prefix in ip_names or looks_like_component(prefix):
            component_names.append(prefix)

    for pin in pins:
        if pin.peripheral:
            component_names.append(pin.peripheral)

    component_names = unique_preserving_order(component_names)
    pin_map: dict[str, list[int]] = defaultdict(list)
    for pin in pins:
        pin_map[pin.peripheral].append(pin.index)

    components: list[ComponentConfig] = []
    for name in sorted(component_names, key=component_sort_key):
        cfg = scoped(raw, name)
        components.append(ComponentConfig(
            name=name,
            kind=component_kind(name),
            config=dict(sorted(cfg.items())),
            pin_indices=tuple(pin_map.get(name, [])),
        ))
    return components


def looks_like_component(prefix: str) -> bool:
    if not prefix:
        return False
    if prefix.startswith("VP_"):
        return False
    if re.match(r"^[A-Z][A-Z0-9_]*\d[A-Z0-9_]*$", prefix):
        return True
    return prefix in SPECIAL_COMPONENT_PREFIXES


def component_sort_key(name: str) -> tuple[str, int, str]:
    match = re.match(r"^([A-Z_]+?)(\d+)(.*)$", name)
    if match:
        return match.group(1), int(match.group(2)), match.group(3)
    return name, 0, ""


def component_kind(name: str) -> str:
    for prefix in sorted(SIGNAL_INSTANCE_PREFIXES, key=len, reverse=True):
        if re.match(rf"^{re.escape(prefix)}\d", name):
            return prefix
    for prefix in sorted(SIGNAL_PREFIXES_WITHOUT_INSTANCE, key=len, reverse=True):
        if name == prefix or name.startswith(prefix + "_"):
            return prefix
    return re.sub(r"\d.*$", "", name) or name


def extract_nvic(raw: Mapping[str, str]) -> tuple[list[NvicConfig], dict[str, str]]:
    parsed: list[NvicConfig] = []
    raw_nvic = scoped(raw, "NVIC")
    for irq, value in sorted(raw_nvic.items()):
        parts = value.split(":")
        enabled = parse_bool(parts[0]) if parts else False
        preempt = parse_int(parts[1]) if len(parts) > 1 else None
        sub = parse_int(parts[2]) if len(parts) > 2 else None
        if irq.endswith("IRQn") or (parts and parts[0].lower() in {"true", "false"}):
            parsed.append(NvicConfig(
                irq=irq,
                enabled=enabled,
                preempt_priority=preempt,
                sub_priority=sub,
                raw=value,
            ))
    return parsed, dict(sorted(raw_nvic.items()))


def extract_dma(raw: Mapping[str, str]) -> tuple[list[DmaRequestConfig], dict[str, str]]:
    raw_dma = scoped(raw, "DMA")
    grouped: dict[int, dict[str, str]] = defaultdict(dict)
    for full_key, value in raw.items():
        match = DMA_INDEXED_RE.match(full_key)
        if match:
            field, index = match.group(1), int(match.group(2))
            grouped[index][field] = value
    requests: list[DmaRequestConfig] = []
    for index in sorted(grouped):
        fields = dict(sorted(grouped[index].items()))
        requests.append(DmaRequestConfig(
            index=index,
            request=fields.get("Request", ""),
            channel=fields.get("Channel", "") or fields.get("Stream", ""),
            direction=fields.get("Direction", ""),
            priority=fields.get("Priority", ""),
            config=fields,
        ))
    return requests, dict(sorted(raw_dma.items()))
