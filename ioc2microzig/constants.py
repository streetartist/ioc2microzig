"""Constants and CubeMX naming patterns used by the parser."""

from __future__ import annotations

import re

import json
import os
import re
import shutil
import sys
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence


PHYSICAL_PIN_RE = re.compile(r"^P([A-Z])([0-9]|1[0-5])(?:[-_].*)?$")
VIRTUAL_PIN_RE = re.compile(r"^VP_[A-Za-z0-9_]+$")
KEY_VALUE_RE = re.compile(r"^([^=#;\s][^=]*?)=(.*)$")
DMA_INDEXED_RE = re.compile(r"^DMA\.([A-Za-z_]+)(\d+)$")
PERIPHERAL_NUMBERED_RE = re.compile(r"^([A-Z]+[A-Z_]*?\d+[A-Z]?)(?:_|$)")

RESERVED_ZIG = {
    "addrspace", "align", "allowzero", "and", "anyframe", "anytype", "asm",
    "async", "await", "break", "callconv", "catch", "comptime", "const",
    "continue", "defer", "else", "enum", "errdefer", "error", "export",
    "extern", "fn", "for", "if", "inline", "noalias", "noinline", "nosuspend",
    "opaque", "or", "orelse", "packed", "pub", "resume", "return", "linksection",
    "struct", "suspend", "switch", "test", "threadlocal", "try", "union",
    "unreachable", "usingnamespace", "var", "volatile", "while",
}

META_PREFIXES = {
    "File", "KeepUserPlacement", "MxDb", "MxCube", "MxToolkit", "ProjectManager",
    "PinOutPanel", "Board", "CAD", "SH", "VP", "NVIC", "DMA", "Mcu",
}

SPECIAL_COMPONENT_PREFIXES = {
    "RCC", "SYS", "GPIO", "CORTEX", "DEBUG", "PWR", "RTC", "TAMP",
    "USB_DEVICE", "USB_HOST", "FREERTOS", "LWIP", "FATFS", "LIBJPEG",
    "MBEDTLS", "MOTORCONTROL", "OPENAMP", "STSAFE", "THREADX", "USBPD",
}

SIGNAL_PREFIXES_WITHOUT_INSTANCE = [
    "USB_OTG_FS", "USB_OTG_HS", "USB", "FMC", "FSMC", "QUADSPI", "OCTOSPI1",
    "OCTOSPI2", "OCTOSPI", "SDMMC1", "SDMMC2", "SDIO", "ETH", "DCMI", "LTDC",
    "JPEG", "RNG", "HASH", "CRYP", "PWR", "RCC", "SYS", "GPIO", "EVENTOUT",
]

SIGNAL_INSTANCE_PREFIXES = [
    "FDCAN", "LPUART", "USART", "UART", "I2C", "I2S", "SPI", "SAI", "TIM",
    "LPTIM", "ADC", "DAC", "COMP", "OPAMP", "CAN", "CEC", "DFSDM", "DFSDMFLT",
    "SAI", "SPDIFRX", "MDIOS", "DMA", "BDMA", "MDMA", "DMA2D",
]
