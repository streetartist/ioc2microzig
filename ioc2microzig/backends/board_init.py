"""Dispatch board_init generation to the selected family backend."""

from __future__ import annotations

from typing import Sequence

from ..models import IocConfig, PinConfig
from .registry import normalize_backend_name, select_auto_backend
from .families import data, generic_pins, stm32f1, stm32f4


def render_board_init_zig(cfg: IocConfig, pins: Sequence[PinConfig], gpio_api: str) -> str:
    if gpio_api == "auto":
        gpio_api = select_auto_backend(cfg)
    else:
        gpio_api = normalize_backend_name(gpio_api)

    if gpio_api == "data":
        return data.render()
    if gpio_api == "hal":
        return stm32f1.render(cfg, pins)
    if gpio_api == "registers":
        return stm32f4.render(cfg, pins)
    if gpio_api == "pins":
        return generic_pins.render(cfg, pins)
    raise ValueError(f"unsupported gpio api: {gpio_api}")
