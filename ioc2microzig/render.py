"""Render MicroZig-oriented Zig project files from parsed CubeMX data."""

from __future__ import annotations

import json
import os
from typing import Sequence

from .backends.board_init import render_board_init_zig
from .models import IocConfig, PinConfig
from .utils import normalize_chip_name, unique_zig_identifiers, zig_bool, zig_identifier, zig_optional_int, zig_optional_pin, zig_optional_port, zig_string

def render_build_zig(project_name: str, target_expr: str) -> str:
    name = zig_identifier(project_name, lower=True)
    return f'''\
const std = @import("std");
const microzig = @import("microzig");

const MicroBuild = microzig.MicroBuild(.{{
    .stm32 = true,
}});

pub fn build(b: *std.Build) void {{
    const optimize = b.standardOptimizeOption(.{{}});
    const mz_dep = b.dependency("microzig", .{{}});
    const mb = MicroBuild.init(b, mz_dep) orelse return;
    const stm32 = mb.ports.stm32;

    const fw = mb.add_firmware(.{{
        .name = "{zig_string(name)}",
        .target = {target_expr},
        .optimize = optimize,
        .root_source_file = b.path("src/main.zig"),
    }});

    mb.install_firmware(fw, .{{}});
    mb.install_firmware(fw, .{{ .format = .elf }});
}}
'''


def render_build_zon(project_name: str, microzig_path: str) -> str:
    name = zig_identifier(project_name, lower=True)
    fingerprint = package_fingerprint(name)
    return f'''\
.{{
    .name = .{name},
    .version = "0.0.0",
    .fingerprint = 0x{fingerprint:016x},
    .dependencies = .{{
        // Keep this path dependency local and reproducible. Replace with a
        // pinned .url/.hash dependency when you standardize on a MicroZig release.
        .microzig = .{{ .path = "{zig_string(microzig_path)}" }},
    }},
    .paths = .{{
        "build.zig",
        "build.zig.zon",
        "src",
    }},
}}
'''


def package_fingerprint(name: str) -> int:
    # Zig 0.15+ requires a package fingerprint in build.zig.zon. Keep it stable
    # for reproducible generated output while avoiding a hard-coded template id.
    import hashlib

    digest = hashlib.blake2s(f"ioc2microzig:{name}".encode("utf-8"), digest_size=4).digest()
    suffix = int.from_bytes(digest, "big") or 1
    return (0x143F5F65 << 32) | suffix


def render_main_zig() -> str:
    return '''\
const board_init = @import("board_init.zig");
const app = @import("app.zig");

pub fn main() !void {
    try board_init.init();
    try app.run();
}
'''


def render_app_zig(pins: Sequence[PinConfig]) -> str:
    led_hint = first_pin_alias_hint(pins, ["led", "green", "red", "blue", "ld"])
    button_hint = first_pin_alias_hint(pins, ["button", "btn", "key", "user"])
    hints = []
    if led_hint:
        hints.append(f"    _ = board.pins.{led_hint}; // Example: generated LED pin alias.")
    if button_hint:
        hints.append(f"    _ = board.pins.{button_hint}; // Example: generated button pin alias.")
    if not hints:
        hints.append("    _ = board.pins; // Generated pin aliases live here.")
    return f'''\
const board = @import("board.zig");
const board_init = @import("board_init.zig");
// USER CODE BEGIN app.imports
// USER CODE END app.imports

// USER CODE BEGIN app.decls
// USER CODE END app.decls

pub fn run() !void {{
{chr(10).join(hints)}
    _ = board_init.pins; // Runtime pin handles initialized by board_init.init().
    _ = board_init.pwm; // Generated PWM helpers, when CubeMX config contains PWM.
    // USER CODE BEGIN app.run.setup
    // USER CODE END app.run.setup

    while (true) {{
        // USER CODE BEGIN app.run.loop
        asm volatile ("nop");
        // USER CODE END app.run.loop
    }}
}}
'''


def first_pin_alias_hint(pins: Sequence[PinConfig], tokens: Sequence[str]) -> str:
    aliases = unique_zig_identifiers([p.zig_name_seed for p in pins])
    for alias, pin in zip(aliases, pins):
        haystack = f"{pin.label} {pin.signal} {alias}".lower()
        if any(token in haystack for token in tokens):
            return alias
    return ""


def render_cubemx_zig(cfg: IocConfig, pins: Sequence[PinConfig]) -> str:
    pin_lines = []
    selected_pin_indices = {p.index for p in pins}
    for p in cfg.pins:
        if p.index not in selected_pin_indices:
            continue
        pin_lines.append(
            "    .{ "
            f".name = \"{zig_string(p.name)}\", "
            f".ioc_key = \"{zig_string(p.ioc_key)}\", "
            f".is_virtual = {zig_bool(p.is_virtual)}, "
            f".port = {zig_optional_port(p.port)}, "
            f".number = {zig_optional_pin(p.number)}, "
            f".signal = \"{zig_string(p.signal)}\", "
            f".label = \"{zig_string(p.label)}\", "
            f".peripheral = \"{zig_string(p.peripheral)}\", "
            f".locked = {zig_bool(p.locked)}, "
            ".gpio = .{ "
            f".mode = \"{zig_string(p.gpio_mode)}\", "
            f".pull = \"{zig_string(p.gpio_pull)}\", "
            f".speed = \"{zig_string(p.gpio_speed)}\", "
            f".output_type = \"{zig_string(p.gpio_output_type)}\", "
            f".output_level = \"{zig_string(p.gpio_output_level)}\" "
            "} },"
        )

    raw_lines = [f'    .{{ .key = "{zig_string(k)}", .value = "{zig_string(v)}" }},' for k, v in cfg.raw.items()]
    rcc_lines = [f'    .{{ .key = "{zig_string(k)}", .value = "{zig_string(v)}" }},' for k, v in cfg.rcc.items()]
    nvic_lines = [
        "    .{ "
        f".irq = \"{zig_string(n.irq)}\", "
        f".enabled = {zig_bool(n.enabled)}, "
        f".preempt_priority = {zig_optional_int(n.preempt_priority)}, "
        f".sub_priority = {zig_optional_int(n.sub_priority)}, "
        f".raw = \"{zig_string(n.raw)}\" "
        "},"
        for n in cfg.nvic
    ]

    dma_config_entries: list[tuple[str, str]] = []
    dma_lines = []
    for req in cfg.dma:
        start = len(dma_config_entries)
        for k, v in req.config.items():
            dma_config_entries.append((f"{req.index}.{k}", v))
        dma_lines.append(
            "    .{ "
            f".index = {req.index}, "
            f".request = \"{zig_string(req.request)}\", "
            f".channel = \"{zig_string(req.channel)}\", "
            f".direction = \"{zig_string(req.direction)}\", "
            f".priority = \"{zig_string(req.priority)}\", "
            f".config_start = {start}, "
            f".config_count = {len(req.config)} "
            "},"
        )
    dma_cfg_lines = [f'    .{{ .key = "{zig_string(k)}", .value = "{zig_string(v)}" }},' for k, v in dma_config_entries]

    component_pin_indices: list[int] = []
    component_config: list[tuple[str, str]] = []
    comp_lines = []
    selected_lookup = {p.index: idx for idx, p in enumerate(pins)}
    for comp in cfg.components:
        pin_start = len(component_pin_indices)
        for original_pin_index in comp.pin_indices:
            if original_pin_index in selected_lookup:
                component_pin_indices.append(selected_lookup[original_pin_index])
        cfg_start = len(component_config)
        for k, v in comp.config.items():
            component_config.append((f"{comp.name}.{k}", v))
        comp_lines.append(
            "    .{ "
            f".name = \"{zig_string(comp.name)}\", "
            f".kind = \"{zig_string(comp.kind)}\", "
            f".pin_start = {pin_start}, "
            f".pin_count = {len(component_pin_indices) - pin_start}, "
            f".config_start = {cfg_start}, "
            f".config_count = {len(comp.config)} "
            "},"
        )
    comp_pin_lines = [f"    {idx}," for idx in component_pin_indices]
    comp_cfg_lines = [f'    .{{ .key = "{zig_string(k)}", .value = "{zig_string(v)}" }},' for k, v in component_config]

    return f'''\
const std = @import("std");

pub const GpioConfig = struct {{
    mode: []const u8,
    pull: []const u8,
    speed: []const u8,
    output_type: []const u8,
    output_level: []const u8,
}};

pub const Pin = struct {{
    name: []const u8,
    ioc_key: []const u8,
    is_virtual: bool,
    port: ?u8,
    number: ?u8,
    signal: []const u8,
    label: []const u8,
    peripheral: []const u8,
    locked: bool,
    gpio: GpioConfig,
}};

pub const Component = struct {{
    name: []const u8,
    kind: []const u8,
    pin_start: usize,
    pin_count: usize,
    config_start: usize,
    config_count: usize,
}};

pub const NvicIrq = struct {{
    irq: []const u8,
    enabled: bool,
    preempt_priority: ?i32,
    sub_priority: ?i32,
    raw: []const u8,
}};

pub const DmaRequest = struct {{
    index: usize,
    request: []const u8,
    channel: []const u8,
    direction: []const u8,
    priority: []const u8,
    config_start: usize,
    config_count: usize,
}};

pub const KeyValue = struct {{
    key: []const u8,
    value: []const u8,
}};

pub const chip = struct {{
    pub const cubemx_name = "{zig_string(cfg.mcu_name)}";
    pub const cpn = "{zig_string(cfg.mcu_cpn)}";
    pub const family = "{zig_string(cfg.mcu_family)}";
    pub const package = "{zig_string(cfg.package)}";
    pub const project = "{zig_string(cfg.project_name)}";
}};

pub const pin_table = [_]Pin{{
{join_or_comment(pin_lines, "    // No selected pins.")}
}};

pub const component_table = [_]Component{{
{join_or_comment(comp_lines, "    // No components discovered.")}
}};

pub const component_pin_indices = [_]usize{{
{join_or_comment(comp_pin_lines, "    // No component-to-pin relationships.")}
}};

pub const component_config = [_]KeyValue{{
{join_or_comment(comp_cfg_lines, "    // No component config entries.")}
}};

pub const rcc_config = [_]KeyValue{{
{join_or_comment(rcc_lines, "    // No RCC entries found.")}
}};

pub const nvic_table = [_]NvicIrq{{
{join_or_comment(nvic_lines, "    // No NVIC IRQ entries found.")}
}};

pub const dma_table = [_]DmaRequest{{
{join_or_comment(dma_lines, "    // No indexed DMA requests found.")}
}};

pub const dma_config = [_]KeyValue{{
{join_or_comment(dma_cfg_lines, "    // No DMA config entries found.")}
}};

pub const raw_ioc = [_]KeyValue{{
{join_or_comment(raw_lines, "    // Empty .ioc file.")}
}};

pub fn pin(comptime index: usize) Pin {{
    return pin_table[index];
}}

pub fn component(comptime index: usize) Component {{
    return component_table[index];
}}

pub fn componentPins(comptime c: Component) []const usize {{
    return component_pin_indices[c.pin_start .. c.pin_start + c.pin_count];
}}

pub fn componentConfig(comptime c: Component) []const KeyValue {{
    return component_config[c.config_start .. c.config_start + c.config_count];
}}

pub fn dmaConfig(comptime d: DmaRequest) []const KeyValue {{
    return dma_config[d.config_start .. d.config_start + d.config_count];
}}

pub fn findPin(comptime name_or_label: []const u8) ?Pin {{
    inline for (pin_table) |p| {{
        if (std.mem.eql(u8, p.name, name_or_label) or
            std.mem.eql(u8, p.ioc_key, name_or_label) or
            std.mem.eql(u8, p.label, name_or_label))
        {{
            return p;
        }}
    }}
    return null;
}}

pub fn findComponent(comptime name: []const u8) ?Component {{
    inline for (component_table) |c| {{
        if (std.mem.eql(u8, c.name, name)) return c;
    }}
    return null;
}}
'''


def join_or_comment(lines: Sequence[str], comment: str) -> str:
    return "\n".join(lines) if lines else comment


def render_board_zig(cfg: IocConfig, pins: Sequence[PinConfig]) -> str:
    pin_aliases = unique_zig_identifiers([p.zig_name_seed for p in pins])
    pin_lines = [f"    pub const {alias} = cubemx.pin({i}); // {p.name}: {zig_string(p.signal or p.ioc_key)}" for i, (alias, p) in enumerate(zip(pin_aliases, pins))]

    component_aliases = unique_zig_identifiers([c.name for c in cfg.components])
    comp_lines = [f"    pub const {alias} = cubemx.component({i}); // {zig_string(c.name)}" for i, (alias, c) in enumerate(zip(component_aliases, cfg.components))]

    return f'''\
pub const cubemx = @import("cubemx.zig");

pub const chip = cubemx.chip;
pub const raw_ioc = cubemx.raw_ioc;
pub const dma = cubemx.dma_table;
pub const nvic = cubemx.nvic_table;
pub const rcc = cubemx.rcc_config;

pub const pins = struct {{
{join_or_comment(pin_lines, "    // No selected pin aliases.")}
}};

pub const peripherals = struct {{
{join_or_comment(comp_lines, "    // No peripheral aliases.")}
}};

pub fn pin(comptime name_or_label: []const u8) ?cubemx.Pin {{
    return cubemx.findPin(name_or_label);
}}

pub fn peripheral(comptime name: []const u8) ?cubemx.Component {{
    return cubemx.findComponent(name);
}}
'''


def render_peripherals_zig(cfg: IocConfig, pins: Sequence[PinConfig]) -> str:
    component_aliases = unique_zig_identifiers([c.name for c in cfg.components])
    reserved_init_fns = {"initAll", "initClocks", "initGpioDefaults", "initDma", "initNvic"}
    init_fns = []
    for alias in component_aliases:
        fn_name = f"init{upper_camel(alias)}"
        if fn_name in reserved_init_fns:
            fn_name = f"initComponent{upper_camel(alias)}"
        init_fns.append(fn_name)
    calls = [f"    try {fn_name}();" for fn_name in init_fns]
    functions: list[str] = []
    selected_index_by_original = {p.index: idx for idx, p in enumerate(pins)}
    for comp, alias, fn_name in zip(cfg.components, component_aliases, init_fns):
        pin_comments = []
        for original_idx in comp.pin_indices:
            if original_idx not in selected_index_by_original:
                continue
            p = cfg.pins[original_idx]
            pin_comments.append(f"    // - {p.name:<5} {p.signal or '-'} {('label=' + p.label) if p.label else ''}")
        cfg_comments = [f"    // - {k} = {v}" for k, v in list(comp.config.items())[:20]]
        if len(comp.config) > 20:
            cfg_comments.append(f"    // - ... {len(comp.config) - 20} more entries are in cubemx.componentConfig(self)")
        if not pin_comments:
            pin_comments = ["    // - No pins mapped to this component in the selected output."]
        if not cfg_comments:
            cfg_comments = ["    // - No component-specific CubeMX config entries."]
        functions.append(f'''\
pub fn {fn_name}() !void {{
    const self = board.peripherals.{alias};
    _ = self;
    // CubeMX component: {zig_string(comp.name)} ({zig_string(comp.kind)})
    // Pins:
{chr(10).join(pin_comments)}
    // Config:
{chr(10).join(cfg_comments)}
    // USER CODE BEGIN peripherals.{fn_name}
    // USER CODE END peripherals.{fn_name}
    // TODO: Replace this stub with family-specific MicroZig HAL setup.
}}
''')

    return f'''\
const board = @import("board.zig");
const cubemx = @import("cubemx.zig");
// USER CODE BEGIN peripherals.imports
// USER CODE END peripherals.imports

// USER CODE BEGIN peripherals.decls
// USER CODE END peripherals.decls

pub fn initAll() !void {{
    try initClocks();
    try initGpioDefaults();
    try initDma();
    try initNvic();
{join_or_comment(calls, "    // No generated peripheral init stubs.")}
    // USER CODE BEGIN peripherals.initAll
    // USER CODE END peripherals.initAll
}}

pub fn initClocks() !void {{
    _ = board.rcc;
    // RCC entries are preserved in board.rcc and cubemx.rcc_config.
    // Keep this function as the single place where you port the CubeMX clock tree
    // to the MicroZig HAL for your STM32 family.
    // USER CODE BEGIN peripherals.initClocks
    // USER CODE END peripherals.initClocks
}}

pub fn initGpioDefaults() !void {{
    _ = board.pins;
    // Pin direction/pull/speed/default-level metadata is in cubemx.pin_table.
    // Use board.pins.<alias> from application code and program GPIO here when
    // the exact MicroZig GPIO API for your chip family is selected.
    // USER CODE BEGIN peripherals.initGpioDefaults
    // USER CODE END peripherals.initGpioDefaults
}}

pub fn initDma() !void {{
    _ = board.dma;
    // DMA requests are preserved in board.dma and cubemx.dmaConfig(...).
    // USER CODE BEGIN peripherals.initDma
    // USER CODE END peripherals.initDma
}}

pub fn initNvic() !void {{
    _ = board.nvic;
    // NVIC priorities/enables are preserved in board.nvic.
    // USER CODE BEGIN peripherals.initNvic
    // USER CODE END peripherals.initNvic
}}

{chr(10).join(functions)}
'''


def upper_camel(value: str) -> str:
    parts = [p for p in value.split("_") if p]
    return "".join(p[:1].upper() + p[1:] for p in parts) or "Unnamed"


def render_pin_manifest_zig() -> str:
    return '''\
// Compatibility shim for older generated projects.
const cubemx = @import("cubemx.zig");

pub const GpioConfig = cubemx.GpioConfig;
pub const Pin = cubemx.Pin;
pub const Component = cubemx.Component;
pub const NvicIrq = cubemx.NvicIrq;
pub const DmaRequest = cubemx.DmaRequest;
pub const KeyValue = cubemx.KeyValue;

pub const chip = cubemx.chip;
pub const pin_table = cubemx.pin_table;
pub const component_table = cubemx.component_table;
pub const component_pin_indices = cubemx.component_pin_indices;
pub const component_config = cubemx.component_config;
pub const rcc_config = cubemx.rcc_config;
pub const nvic_table = cubemx.nvic_table;
pub const dma_table = cubemx.dma_table;
pub const dma_config = cubemx.dma_config;
pub const raw_ioc = cubemx.raw_ioc;

pub const pin = cubemx.pin;
pub const component = cubemx.component;
pub const componentPins = cubemx.componentPins;
pub const componentConfig = cubemx.componentConfig;
pub const dmaConfig = cubemx.dmaConfig;
pub const findPin = cubemx.findPin;
pub const findComponent = cubemx.findComponent;
'''


def render_readme(cfg: IocConfig, pins: Sequence[PinConfig], target_expr: str, gpio_api: str) -> str:
    peripheral_summary = {
        comp.name: {
            "kind": comp.kind,
            "pins": [cfg.pins[i].name for i in comp.pin_indices],
            "config_entries": len(comp.config),
        }
        for comp in cfg.components
    }
    return f'''\
# {cfg.project_name} - Zig board skeleton generated from STM32CubeMX

Source `.ioc`: `{cfg.path.name}`

## Detected MCU

- CubeMX MCU: `{cfg.mcu_name or "unknown"}`
- CubeMX CPN: `{cfg.mcu_cpn or "unknown"}`
- Family: `{cfg.mcu_family or "unknown"}`
- Package: `{cfg.package or "unknown"}`
- MicroZig target expression: `{target_expr}`
- Init backend: `{gpio_api}`

## Generated source layout

- `src/cubemx.zig`: typed tables for all converted CubeMX data.
- `src/board.zig`: stable aliases for application code, e.g. `board.pins.<label>` and `board.peripherals.<name>`.
- `src/peripherals.zig`: one init stub per discovered component/peripheral.
- `src/board_init.zig`: central board initialization entrypoint.
- `src/app.zig`: application code entrypoint where you start writing firmware logic.
- `cubemx.ioc.json`: lossless JSON form of the parsed `.ioc`.

## Build

1. Install the Zig version expected by your MicroZig checkout.
2. Clone MicroZig and update `build.zig.zon` if `.microzig.path` is wrong.
3. Run:

```sh
zig build
```

Firmware artifacts are installed under `zig-out/firmware`.

## Development workflow

Application code should import `board.zig`:

```zig
const board = @import("board.zig");

pub fn run() !void {{
    _ = board.pins;        // generated aliases from CubeMX labels/signals
    _ = board.peripherals; // USART/I2C/SPI/TIM/ADC/etc. manifest
}}
```

The default `--gpio-api auto` mode tries to convert CubeMX initialization into MicroZig code. Backend names are `data`, `hal`, `registers`, and `pins`; legacy names such as `manifest`, `f1-runtime`, `f4-basic`, and `pins-v2` are accepted for compatibility. Use `--gpio-api data` when you only want portable metadata tables and stubs.

## Regeneration-safe user code

`src/app.zig`, `src/board_init.zig`, and `src/peripherals.zig` contain CubeMX-style user regions:

```zig
// USER CODE BEGIN app.run.loop
// USER CODE END app.run.loop
```

When you regenerate with `--force`, only code between matching `USER CODE BEGIN/END` markers is preserved. Generated code outside those regions may be replaced.

## Review items before flashing hardware

- Verify the generated MicroZig target expression in `build.zig`.
- Review generated `src/board_init.zig` before flashing hardware.
- Verify alternate-function numbers if using `--gpio-api pins` or a register-level backend; CubeMX `.ioc` files do not expose AF data uniformly.
- Fill in unsupported peripherals left as TODOs in `src/peripherals.zig`.

## Selected pins

| Pin | IOC key | Signal | Label | Peripheral | GPIO mode | Pull |
| --- | --- | --- | --- | --- | --- | --- |
{os.linesep.join(f"| `{p.name}` | `{p.ioc_key}` | `{p.signal or '-'}` | `{p.label or '-'}` | `{p.peripheral}` | `{p.gpio_mode or '-'}` | `{p.gpio_pull or '-'}` |" for p in pins) if pins else "| - | - | - | - | - | - | - |"}

## Component summary

```json
{json.dumps(peripheral_summary, indent=2, ensure_ascii=False)}
```
'''
