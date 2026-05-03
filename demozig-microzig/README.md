# demozig - Zig board skeleton generated from STM32CubeMX

Source `.ioc`: `demozig.ioc`

## Detected MCU

- CubeMX MCU: `STM32F103C(8-B)Tx`
- CubeMX CPN: `STM32F103C8T6`
- Family: `STM32F1`
- Package: `LQFP48`
- MicroZig target expression: `stm32.chips.STM32F103C8`
- Init backend: `auto`

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

pub fn run() !void {
    _ = board.pins;        // generated aliases from CubeMX labels/signals
    _ = board.peripherals; // USART/I2C/SPI/TIM/ADC/etc. manifest
}
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
| `PA13` | `PA13` | `SYS_JTMS-SWDIO` | `-` | `SYS` | `Serial_Wire` | `-` |
| `PA14` | `PA14` | `SYS_JTCK-SWCLK` | `-` | `SYS` | `Serial_Wire` | `-` |
| `PC13` | `PC13-TAMPER-RTC` | `GPIO_Output` | `-` | `GPIO` | `-` | `-` |
| `PC14` | `PC14-OSC32_IN` | `RCC_OSC32_IN` | `-` | `RCC` | `LSE-External-Oscillator` | `-` |
| `PC15` | `PC15-OSC32_OUT` | `RCC_OSC32_OUT` | `-` | `RCC` | `LSE-External-Oscillator` | `-` |
| `PD0` | `PD0-OSC_IN` | `RCC_OSC_IN` | `-` | `RCC` | `HSE-External-Oscillator` | `-` |
| `PD1` | `PD1-OSC_OUT` | `RCC_OSC_OUT` | `-` | `RCC` | `HSE-External-Oscillator` | `-` |
| `VP_SYS_VS_Systick` | `VP_SYS_VS_Systick` | `SYS_VS_Systick` | `-` | `SYS` | `SysTick` | `-` |

## Component summary

```json
{
  "GPIO": {
    "kind": "GPIO",
    "pins": [
      "PC13"
    ],
    "config_entries": 1
  },
  "NVIC": {
    "kind": "NVIC",
    "pins": [],
    "config_entries": 11
  },
  "RCC": {
    "kind": "RCC",
    "pins": [
      "PC14",
      "PC15",
      "PD0",
      "PD1"
    ],
    "config_entries": 21
  },
  "SYS": {
    "kind": "SYS",
    "pins": [
      "PA13",
      "PA14",
      "VP_SYS_VS_Systick"
    ],
    "config_entries": 0
  }
}
```
