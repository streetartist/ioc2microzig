"""Filesystem project writer and summary reporting."""

from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Sequence

from .models import IocConfig, PinConfig
from .render import (
    render_app_zig,
    render_board_init_zig,
    render_board_zig,
    render_build_zig,
    render_build_zon,
    render_cubemx_zig,
    render_main_zig,
    render_peripherals_zig,
    render_pin_manifest_zig,
    render_readme,
)
from .user_code import merge_user_regions

PRESERVE_USER_CODE = {
    "src/app.zig",
    "src/board_init.zig",
    "src/peripherals.zig",
}

def build_json(cfg: IocConfig, selected: Sequence[PinConfig]) -> dict[str, object]:
    selected_indices = {p.index for p in selected}
    return {
        "project": cfg.project_name,
        "mcu_name": cfg.mcu_name,
        "mcu_cpn": cfg.mcu_cpn,
        "mcu_family": cfg.mcu_family,
        "package": cfg.package,
        "ip_names": cfg.ip_names,
        "selected_pins": [
            {
                "index": p.index,
                "ioc_key": p.ioc_key,
                "name": p.name,
                "is_virtual": p.is_virtual,
                "port": p.port,
                "number": p.number,
                "signal": p.signal,
                "label": p.label,
                "peripheral": p.peripheral,
                "gpio_mode": p.gpio_mode,
                "gpio_pull": p.gpio_pull,
                "gpio_speed": p.gpio_speed,
                "gpio_output_type": p.gpio_output_type,
                "gpio_output_level": p.gpio_output_level,
                "locked": p.locked,
                "raw": dict(p.user_keys),
            }
            for p in selected
        ],
        "components": [
            {
                "name": c.name,
                "kind": c.kind,
                "pins": [cfg.pins[i].name for i in c.pin_indices if i in selected_indices],
                "config": dict(c.config),
            }
            for c in cfg.components
        ],
        "rcc": cfg.rcc,
        "nvic": [n.__dict__ for n in cfg.nvic],
        "nvic_raw": cfg.nvic_raw,
        "dma": [
            {
                "index": d.index,
                "request": d.request,
                "channel": d.channel,
                "direction": d.direction,
                "priority": d.priority,
                "config": dict(d.config),
            }
            for d in cfg.dma
        ],
        "dma_raw": cfg.dma_raw,
        "raw": dict(cfg.raw),
    }


def write_project(
    cfg: IocConfig,
    out_dir: Path,
    include: set[str],
    target_expr: str,
    gpio_api: str,
    microzig_path: str,
    force: bool,
    copy_ioc: bool,
) -> None:
    selected = cfg.selected_pins(include)
    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        raise SystemExit(f"Output directory {out_dir} already exists and is not empty. Use --force to overwrite generated files.")

    src = out_dir / "src"
    src.mkdir(parents=True, exist_ok=True)

    files = {
        out_dir / "build.zig": render_build_zig(cfg.project_name, target_expr),
        out_dir / "build.zig.zon": render_build_zon(cfg.project_name, microzig_path),
        out_dir / "README.md": render_readme(cfg, selected, target_expr, gpio_api),
        src / "main.zig": render_main_zig(),
        src / "app.zig": render_app_zig(selected),
        src / "cubemx.zig": render_cubemx_zig(cfg, selected),
        src / "board.zig": render_board_zig(cfg, selected),
        src / "peripherals.zig": render_peripherals_zig(cfg, selected),
        src / "board_init.zig": render_board_init_zig(cfg, selected, gpio_api),
        src / "pin_manifest.zig": render_pin_manifest_zig(),
        out_dir / "cubemx.ioc.json": json.dumps(build_json(cfg, selected), indent=2, ensure_ascii=False) + "\n",
    }

    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        rel = path.relative_to(out_dir).as_posix()
        if rel in PRESERVE_USER_CODE and path.exists():
            previous = path.read_text(encoding="utf-8")
            content, missing = merge_user_regions(content, previous)
            for name in missing:
                print(f"warning: preserved USER CODE region '{name}' from {rel} has no matching region in regenerated output")
        path.write_text(content, encoding="utf-8")

    if copy_ioc:
        shutil.copy2(cfg.path, out_dir / cfg.path.name)


def print_summary(cfg: IocConfig, selected: Sequence[PinConfig], target_expr: str) -> None:
    print(f"Project:       {cfg.project_name}")
    print(f"MCU:           {cfg.mcu_name or '(unknown)'}")
    print(f"CPN:           {cfg.mcu_cpn or '(unknown)'}")
    print(f"Family:        {cfg.mcu_family or '(unknown)'}")
    print(f"MicroZig tgt:  {target_expr}")
    print(f"Selected pins: {len(selected)} / {len(cfg.pins)}")
    print(f"Components:    {len(cfg.components)}")
    print(f"RCC entries:   {len(cfg.rcc)}")
    print(f"NVIC IRQs:     {len(cfg.nvic)}")
    print(f"DMA requests:  {len(cfg.dma)}")
    print("Peripherals from selected pins:")
    groups: dict[str, int] = defaultdict(int)
    for p in selected:
        groups[p.peripheral] += 1
    for periph, count in sorted(groups.items()):
        print(f"  - {periph}: {count} pin(s)")
