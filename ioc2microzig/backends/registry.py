"""Backend registry for family-specific MicroZig init generation."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import IocConfig
from ..utils import normalize_chip_name


@dataclass(frozen=True)
class InitBackend:
    name: str
    description: str
    template: str


BACKENDS: dict[str, InitBackend] = {
    "data": InitBackend(
        name="data",
        description="portable metadata only; no HAL initialization",
        template="data/board_init.zig.j2",
    ),
    "hal": InitBackend(
        name="hal",
        description="STM32F1 HAL init for RCC, GPIO, TIM PWM, USART/UART",
        template="stm32f1/board_init.zig.j2",
    ),
    "registers": InitBackend(
        name="registers",
        description="STM32F4 register-level GPIO init for chip targets without hal.pins",
        template="stm32f4/board_init.zig.j2",
    ),
    "pins": InitBackend(
        name="pins",
        description="MicroZig hal.pins.GlobalConfiguration backend",
        template="generic/pins_board_init.zig.j2",
    ),
}

BACKEND_ALIASES = {
    "manifest": "data",
    "comments": "data",
    "f1-runtime": "hal",
    "pins-v2": "pins",
    "f4-basic": "registers",
}

CLI_BACKEND_CHOICES = ("auto", "data", "hal", "registers", "pins", "manifest", "comments", "pins-v2", "f1-runtime", "f4-basic")


def normalize_backend_name(name: str) -> str:
    return BACKEND_ALIASES.get(name, name)


def select_auto_backend(cfg: IocConfig) -> str:
    """Choose the best backend for the generated target."""
    chip = normalize_chip_name(cfg.mcu_name, cfg.mcu_cpn)
    if chip.startswith("STM32F1"):
        return "hal"
    if chip.startswith(("STM32F40", "STM32F41", "STM32F42", "STM32F43")):
        return "registers"
    return "pins"
