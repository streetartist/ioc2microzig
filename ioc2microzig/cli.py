"""Command line interface."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional, Sequence

from .backends import CLI_BACKEND_CHOICES
from .parser import parse_ioc
from .project import print_summary, write_project
from .utils import default_target_expr, parse_include, zig_identifier

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a MicroZig-oriented Zig board skeleton from STM32CubeMX .ioc files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("ioc", type=Path, help="Path to the STM32CubeMX .ioc file.")
    parser.add_argument("-o", "--out", type=Path, default=argparse.SUPPRESS, help="Output project directory. Defaults to <project-name>-microzig next to the current working directory.")
    parser.add_argument("--include", default="all", help="Comma-separated pins/peripherals to include: all,gpio,uart,usart,i2c,spi,tim,adc,usb,can or names like USART2.")
    parser.add_argument("--target", default="", help="Override MicroZig target expression, e.g. stm32.boards.stm32f303nucleo or stm32.chips.STM32F103C8.")
    parser.add_argument("--microzig-path", default="../microzig", help="Path written into build.zig.zon for the MicroZig dependency.")
    parser.add_argument("--gpio-api", choices=CLI_BACKEND_CHOICES, default="auto", help="Generated board_init backend: auto, data, hal, registers, or pins. Legacy names are accepted.")
    parser.add_argument("--force", action="store_true", help="Overwrite generated files in a non-empty output directory.")
    parser.add_argument("--summary-only", action="store_true", help="Parse and print a summary without writing files.")
    parser.add_argument("--copy-ioc", action="store_true", help="Copy the source .ioc file into the output directory.")
    return parser


def default_out_dir(project_name: str) -> Path:
    name = zig_identifier(project_name, lower=True).strip("_") or "stm32_project"
    return Path(f"{name.replace('_', '-')}-microzig")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    ioc_path = args.ioc.expanduser().resolve()
    if not ioc_path.exists():
        print(f"error: .ioc file not found: {ioc_path}", file=sys.stderr)
        return 2
    if ioc_path.suffix.lower() != ".ioc":
        print(f"warning: input does not end with .ioc: {ioc_path}", file=sys.stderr)

    cfg = parse_ioc(ioc_path)
    include = parse_include(args.include)
    target_expr = args.target.strip() or default_target_expr(cfg)
    selected = cfg.selected_pins(include)

    print_summary(cfg, selected, target_expr)
    if args.summary_only:
        return 0

    out_dir = (getattr(args, "out", None) or default_out_dir(cfg.project_name)).expanduser().resolve()
    write_project(
        cfg=cfg,
        out_dir=out_dir,
        include=include,
        target_expr=target_expr,
        gpio_api=args.gpio_api,
        microzig_path=args.microzig_path,
        force=args.force,
        copy_ioc=args.copy_ioc,
    )

    print(f"\nGenerated: {out_dir}")
    print("Next:")
    print(f"  cd {out_dir}")
    print("  edit src/app.zig and src/peripherals.zig")
    print("  zig build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
