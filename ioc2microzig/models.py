"""Typed model objects for STM32CubeMX .ioc content."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

@dataclass(frozen=True)
class RawEntry:
    key: str
    value: str
    line: int


@dataclass(frozen=True)
class PinConfig:
    index: int
    ioc_key: str
    name: str
    is_virtual: bool
    port: Optional[str]
    number: Optional[int]
    signal: str = ""
    label: str = ""
    gpio_mode: str = ""
    gpio_pull: str = ""
    gpio_speed: str = ""
    gpio_output_type: str = ""
    gpio_output_level: str = ""
    locked: bool = False
    user_keys: Mapping[str, str] = field(default_factory=dict)

    @property
    def peripheral(self) -> str:
        from .utils import classify_signal
        return classify_signal(self.signal)

    @property
    def zig_name_seed(self) -> str:
        if self.label:
            return self.label
        if self.signal:
            return f"{self.name}_{self.signal}"
        return self.name

    @property
    def gpio_port_field(self) -> str:
        return f"GPIO{self.port}" if self.port else "GPIO?"

    @property
    def pin_field(self) -> str:
        return f"PIN{self.number}" if self.number is not None else "PIN?"


@dataclass(frozen=True)
class ComponentConfig:
    name: str
    kind: str
    config: Mapping[str, str]
    pin_indices: tuple[int, ...]


@dataclass(frozen=True)
class NvicConfig:
    irq: str
    enabled: bool
    preempt_priority: Optional[int]
    sub_priority: Optional[int]
    raw: str


@dataclass(frozen=True)
class DmaRequestConfig:
    index: int
    request: str
    channel: str
    direction: str
    priority: str
    config: Mapping[str, str]


@dataclass
class IocConfig:
    path: Path
    raw: "OrderedDict[str, str]"
    entries: list[RawEntry]
    project_name: str
    mcu_name: str
    mcu_cpn: str
    mcu_family: str
    package: str
    ip_names: list[str]
    pins: list[PinConfig]
    components: list[ComponentConfig]
    rcc: dict[str, str]
    nvic: list[NvicConfig]
    nvic_raw: dict[str, str]
    dma: list[DmaRequestConfig]
    dma_raw: dict[str, str]

    def selected_pins(self, include: set[str]) -> list[PinConfig]:
        if "all" in include:
            return list(self.pins)
        result: list[PinConfig] = []
        for pin in self.pins:
            p = pin.peripheral.lower()
            sig = pin.signal.lower()
            if p in include:
                result.append(pin)
                continue
            for want in include:
                if want in sig:
                    result.append(pin)
                    break
        return result

