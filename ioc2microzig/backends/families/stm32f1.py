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
    all_physical = [p for p in pins if not p.is_virtual and p.port is not None and p.number is not None]
    physical = [p for p in all_physical if p.peripheral not in {"SYS", "RCC"}]
    aliases = unique_zig_identifiers([p.zig_name_seed for p in physical])
    ports = sorted({p.gpio_port_field for p in all_physical})
    periphs = peripheral_clocks(cfg, physical)
    pwm_timers, counter_timers, pwm_outputs = timer_runtime(cfg, physical, aliases)
    return render_template(
        BACKENDS["hal"].template,
        pins=[pin_context(alias, p) for alias, p in zip(aliases, physical)],
        gpio_ports=ports,
        enable_afio=any(pin_uses_alternate_function(p) for p in physical),
        enable_pwr=has_component(cfg, "SYS"),
        swj_remap=swj_remap(cfg.pins),
        peripheral_clocks=periphs,
        rcc=rcc_context(cfg),
        pwm_timers=pwm_timers,
        counter_timers=counter_timers,
        pwm_outputs=pwm_outputs,
        uarts=uart_runtime(cfg),
        i2cs=i2c_runtime(cfg),
        spis=spi_runtime(cfg),
        adcs=adc_runtime(cfg, physical),
        unsupported=unsupported_runtime(cfg),
        rcc_comments=indent_lines(render_rcc_comments(cfg), "    "),
    )


def pin_context(alias: str, p: PinConfig) -> dict[str, object]:
    sig = p.signal.upper()
    mode = p.gpio_mode.upper()
    pull = p.gpio_pull.upper()
    setup: dict[str, object]
    if pin_uses_analog(p):
        setup = {"kind": "input", "mode": "analog", "pull": ""}
    elif sig == "GPIO_OUTPUT" or "OUTPUT" in mode:
        setup = {
            "kind": "output",
            "mode": "general_purpose_open_drain" if pin_is_open_drain(p) else "general_purpose_push_pull",
            "speed": speed_value(p),
            "initial": output_initial_value(p),
        }
    elif sig == "GPIO_INPUT" or "INPUT" in mode:
        if "PULLUP" in pull:
            setup = {"kind": "input", "mode": "pull", "pull": "up"}
        elif "PULLDOWN" in pull:
            setup = {"kind": "input", "mode": "pull", "pull": "down"}
        else:
            setup = {"kind": "input", "mode": "floating", "pull": ""}
    elif pin_uses_alternate_function(p) and not ("RX" in sig or "MISO" in sig):
        mode_name = "alternate_function_open_drain" if pin_is_open_drain(p) or "SCL" in sig or "SDA" in sig else "alternate_function_push_pull"
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
    speed = p.gpio_speed.upper()
    if "HIGH" in speed or "50" in speed:
        return "max_50MHz"
    if "MEDIUM" in speed or "10" in speed:
        return "max_10MHz"
    return "max_2MHz"


def pin_is_open_drain(p: PinConfig) -> bool:
    haystack = f"{p.gpio_output_type} {p.gpio_mode} {p.signal}".upper()
    return "OPEN_DRAIN" in haystack or "_OD" in haystack


def output_initial_value(p: PinConfig) -> str:
    level = p.gpio_output_level.upper()
    if "RESET" in level or "LOW" in level or level == "0":
        return "0"
    if "SET" in level or "HIGH" in level or level == "1":
        return "1"
    return "0"


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


def pin_uses_analog(p: PinConfig) -> bool:
    sig = p.signal.upper()
    mode = p.gpio_mode.upper()
    return "ANALOG" in mode or sig.startswith("ADC") or "_ADC" in sig or sig.startswith("DAC") or "_DAC" in sig


def swj_remap(pins: Sequence[PinConfig]) -> str:
    for pin in pins:
        haystack = f"{pin.signal} {pin.gpio_mode}".upper()
        if "SYS_JTMS-SWDIO" in haystack and "SERIAL_WIRE" in haystack:
            return "Only_SWDP"
    return ""


def peripheral_clock_name(p: PinConfig) -> str:
    haystack = f"{p.peripheral}_{p.signal}".upper()
    match = re.search(r"(TIM\d+|USART\d+|UART\d+|SPI\d+|I2C\d+|ADC\d+|DAC\d+|CAN\d*)", haystack)
    return match.group(1) if match else ""


def peripheral_clocks(cfg: IocConfig, pins: Sequence[PinConfig]) -> list[str]:
    clocks = {peripheral_clock_name(p) for p in pins if peripheral_clock_name(p)}
    for comp in cfg.components:
        name = comp.name.upper()
        if re.match(r"^(TIM|USART|UART|SPI|I2C|ADC|DAC|CAN)\d+$", name):
            clocks.add(name)
    return sorted(clocks)


def timer_runtime(
    cfg: IocConfig,
    pins: Sequence[PinConfig],
    aliases: Sequence[str],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    pwm_timers: list[dict[str, object]] = []
    counter_timers: list[dict[str, object]] = []
    api: list[dict[str, object]] = []
    timer_aliases: dict[str, str] = {}
    periods: dict[str, str] = {}
    for comp in cfg.components:
        timer = comp.name.upper()
        if not re.match(r"^TIM\d+$", timer):
            continue
        channels = pwm_channels(comp.config)
        prescaler = int_expr(first_config(comp.config, ["Prescaler"]), default="0")
        period = int_expr(first_config(comp.config, ["Period", "PeriodNoDither", "AutoReload"]), default="65535")
        if not channels:
            counter_timers.append({
                "alias": zig_identifier(f"{timer}_counter", lower=True),
                "instance": timer,
                "prescaler": prescaler,
                "period": period,
            })
            continue
        alias = zig_identifier(f"{timer}_pwm", lower=True)
        timer_aliases[timer] = alias
        periods[timer] = period
        pwm_timers.append({
            "alias": alias,
            "instance": timer,
            "prescaler": prescaler,
            "period": period,
            "channels": [{"index": channel - 1, "pulse": pwm_pulse(comp.config, channel)} for channel in channels],
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
    return pwm_timers, counter_timers, api


def uart_runtime(cfg: IocConfig) -> list[dict[str, object]]:
    uarts: list[dict[str, object]] = []
    for comp in cfg.components:
        name = comp.name.upper()
        if not re.match(r"^(USART|UART)\d+$", name):
            continue
        alias = zig_identifier(name, lower=True)
        uarts.append({
            "alias": alias,
            "instance": name,
            "baud_rate": int_expr(comp.config.get("BaudRate", ""), default="115200"),
            "stop_bits": uart_stop_bits(comp.config.get("StopBits", "")),
            "parity": uart_parity(comp.config.get("Parity", "")),
            "flow_control": uart_flow_control(comp.config),
            "comments": uart_comments(comp.config),
        })
    return uarts


def i2c_runtime(cfg: IocConfig) -> list[dict[str, object]]:
    i2cs: list[dict[str, object]] = []
    for comp in cfg.components:
        name = comp.name.upper()
        if not re.match(r"^I2C\d+$", name):
            continue
        speed, mode = i2c_speed_mode(comp.config)
        i2cs.append({
            "alias": zig_identifier(name, lower=True),
            "instance": name,
            "speed": speed,
            "mode": mode,
        })
    return i2cs


def spi_runtime(cfg: IocConfig) -> list[dict[str, object]]:
    spis: list[dict[str, object]] = []
    for comp in cfg.components:
        name = comp.name.upper()
        if not re.match(r"^SPI\d+$", name):
            continue
        spis.append({
            "alias": zig_identifier(name, lower=True),
            "instance": name,
            "fields": spi_fields(comp.config),
            "comments": spi_comments(comp.config),
        })
    return spis


def adc_runtime(cfg: IocConfig, pins: Sequence[PinConfig]) -> list[dict[str, object]]:
    channel_map: dict[str, set[int]] = {}
    for pin in pins:
        match = re.search(r"(ADC\d+|ADCX)_INP?(\d+)|ADC_CHANNEL_(\d+)", pin.signal.upper())
        if not match:
            continue
        adc = "ADC1" if match.group(1) == "ADCX" else match.group(1)
        channel = match.group(2) or match.group(3)
        if adc and channel:
            channel_map.setdefault(adc, set()).add(int(channel))
    adcs: list[dict[str, object]] = []
    for comp in cfg.components:
        name = comp.name.upper()
        if not re.match(r"^ADC\d+$", name):
            continue
        channels = sorted(channel_map.get(name, set()) | set(adc_config_channels(comp.config)))
        adcs.append({
            "alias": zig_identifier(name, lower=True),
            "instance": name,
            "channels": channels,
        })
    return adcs


def unsupported_runtime(cfg: IocConfig) -> list[dict[str, str]]:
    unsupported: list[dict[str, str]] = []
    for comp in cfg.components:
        name = comp.name.upper()
        if re.match(r"^DAC\d+$", name):
            unsupported.append({"name": name, "reason": "STM32F1 MicroZig HAL does not expose a DAC driver for this target."})
    return unsupported


def has_component(cfg: IocConfig, name: str) -> bool:
    return any(comp.name.upper() == name.upper() for comp in cfg.components)


def first_config(config: Mapping[str, str], names: Sequence[str]) -> str:
    for name in names:
        value = config.get(name, "")
        if value:
            return value
    return ""


def uart_stop_bits(value: str) -> str:
    text = value.upper()
    if "_2" in text or text.endswith("2"):
        return "two"
    if "1_5" in text or "1.5" in text:
        return "one_and_half"
    if "0_5" in text or "0.5" in text or "HALF" in text:
        return "half"
    return "one"


def uart_parity(value: str) -> str:
    text = value.upper()
    if "EVEN" in text:
        return "even"
    if "ODD" in text:
        return "odd"
    return "none"


def uart_flow_control(config: Mapping[str, str]) -> str:
    haystack = " ".join(f"{k}={v}" for k, v in config.items()).upper()
    has_cts = "CTS" in haystack
    has_rts = "RTS" in haystack
    if has_cts and has_rts:
        return "CTS_RTS"
    if has_cts:
        return "CTS"
    if has_rts:
        return "RTS"
    return "none"


def uart_comments(config: Mapping[str, str]) -> list[str]:
    comments: list[str] = []
    word = config.get("WordLength", "").upper()
    if word and "8" not in word:
        comments.append(f"CubeMX WordLength={word}; STM32F103 MicroZig UART currently exposes 8 data bits.")
    return comments


def i2c_speed_mode(config: Mapping[str, str]) -> tuple[str, str]:
    speed_value = first_config(config, ["ClockSpeed", "I2C_ClockSpeed", "Speed", "I2C_Speed"])
    speed = int_expr(speed_value, default="")
    mode_text = " ".join(f"{k}={v}" for k, v in config.items()).upper()
    if not speed:
        speed = "400000" if "FAST" in mode_text else "100000"
    mode = "fast" if "FAST" in mode_text or (speed.isdigit() and int(speed) > 100000) else "standard"
    return speed, mode


def spi_comments(config: Mapping[str, str]) -> list[str]:
    keys = ["Mode", "Direction", "BaudRatePrescaler", "DataSize", "CLKPolarity", "CLKPhase", "FirstBit"]
    return [f"{key}={config[key]}" for key in keys if key in config]


def spi_fields(config: Mapping[str, str]) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    fields.append({"name": "phase", "value": "SecondEdge" if "2EDGE" in config.get("CLKPhase", "").upper() else "FirstEdge"})
    fields.append({"name": "polarity", "value": "IdleHigh" if "HIGH" in config.get("CLKPolarity", "").upper() else "IdleLow"})
    fields.append({"name": "data_size", "value": "Bits16" if "16" in config.get("DataSize", "").upper() else "Bits8"})
    fields.append({"name": "chip_select", "value": "GPIO"})
    if config.get("BaudRatePrescaler", ""):
        match = re.search(r"_(\d+)$", config["BaudRatePrescaler"].upper())
        if match:
            fields.append({"name": "prescaler", "value": f"Div{match.group(1)}"})
    fields.append({"name": "frame_format", "value": "LSBFirst" if "LSB" in config.get("FirstBit", "").upper() else "MSBFirst"})
    return fields


def adc_config_channels(config: Mapping[str, str]) -> list[int]:
    channels: list[int] = []
    for value in config.values():
        match = re.search(r"ADC_CHANNEL_(\d+)", value.upper())
        if match:
            channels.append(int(match.group(1)))
    return sorted(set(channels))


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


def pwm_pulse(config: Mapping[str, str], channel: int) -> str:
    patterns = [
        rf"^Pulse(?:NoDither)?_{channel}$",
        rf"^Pulse(?:NoDither)?\b.*CH{channel}$",
        rf"^Pulse(?:NoDither)?$",
    ]
    for pattern in patterns:
        for key, value in config.items():
            if re.search(pattern, key, re.IGNORECASE):
                return int_expr(value, default="0")
    return "0"


def int_expr(value: str, *, default: str) -> str:
    text = value.strip()
    if not text:
        return default
    if re.fullmatch(r"[0-9xXa-fA-F+\-*/() ]+", text):
        return text
    return default
