<p align="right">
  <a href="README.md">English</a> | <strong>简体中文</strong>
</p>

<p align="center">
  <img src="logo.png" alt="ioc2microzig logo" width="160">
</p>

<h1 align="center">ioc2microzig</h1>

<p align="center">
  从 STM32CubeMX <code>.ioc</code> 文件生成 MicroZig 项目骨架和板级初始化代码。
</p>

<p align="center">
  <a href="https://github.com/streetartist/ioc2microzig/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/streetartist/ioc2microzig/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-blue">
  <img alt="Status: alpha" src="https://img.shields.io/badge/status-alpha-orange">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
</p>

`ioc2microzig` 读取你已经在 STM32CubeMX 中维护的硬件配置，并把它转换成面向 MicroZig 的 Zig 固件项目。它会保留 CubeMX 元数据，生成稳定的 Zig 别名，在已支持的芯片系列上生成板级初始化代码，并为需要手写的部分留下可重复生成的 `USER CODE` 区域。

它不是 CubeMX C 代码到 Zig 的翻译器；它以 `.ioc` 配置文件作为输入源。

## 目录

- [为什么需要它](#为什么需要它)
- [功能亮点](#功能亮点)
- [当前状态](#当前状态)
- [安装](#安装)
- [快速开始](#快速开始)
- [命令行](#命令行)
- [生成项目结构](#生成项目结构)
- [闪灯示例](#闪灯示例)
- [重新生成工作流](#重新生成工作流)
- [验证](#验证)
- [路线图](#路线图)
- [贡献](#贡献)
- [许可证](#许可证)

## 为什么需要它

STM32CubeMX 仍然是描述 STM32 引脚、时钟和外设配置的高效工具。MicroZig 是很好的 Zig 固件基础，但把 CubeMX 配置手工搬到 Zig 里既重复，又容易出错。

`ioc2microzig` 解决的是这段迁移成本：

- 继续把 `.ioc` 作为可审查的硬件配置文件；
- 生成带 `build.zig` 和 `build.zig.zon` 的 MicroZig 项目；
- 把已支持的 STM32 初始化转换成 Zig；
- 对暂不支持或无法确定的配置保留结构化数据，而不是直接丢弃；
- 允许反复重新生成，同时保留用户手写固件代码。

## 功能亮点

- 把 STM32CubeMX `.ioc` 解析成类型化 Python 模型。
- 生成 MicroZig 项目文件、源码结构和本地 MicroZig 依赖配置。
- 在 `board.zig` 中生成稳定的引脚和外设别名。
- 在 `cubemx.zig` 和 `cubemx.ioc.json` 中保留原始 CubeMX 数据。
- 通过可插拔后端生成不同芯片系列的 `board_init.zig`。
- 通过 CubeMX 风格的 `USER CODE BEGIN/END` 标记，在重新生成时保留用户代码。
- 提供 HAL、寄存器、`hal.pins` 和纯数据多种输出模式。

## 当前状态

`ioc2microzig` 目前是 alpha 软件。STM32F103C8 / Blue Pill 的 `PC13` 闪灯路径已经过实物验证，但烧录真实硬件前仍建议检查生成的初始化代码。

| MCU 系列 | 默认后端 | 当前覆盖 |
| --- | --- | --- |
| STM32F1 | `hal` | RCC、GPIO、TIM counter/PWM、USART/UART、I2C、SPI、ADC 别名和 analog GPIO 配置。 |
| STM32F4/F40x/F41x/F42x/F43x | `registers` | GPIO 时钟、MODER、AFR 寄存器写入。RCC/TIM/UART 细节会保留为 TODO 和 CubeMX 摘要。 |
| 其他 STM32 系列 | `pins` | 尝试生成 `hal.pins.GlobalConfiguration` 和基础 UART v3 初始化。不支持项保留为 TODO。 |

生成器会尽量把不确定或暂不支持的配置保留在生成注释、`cubemx.zig` 和 `cubemx.ioc.json` 中。

## 安装

要求：

- Python 3.10 或更新版本；
- 本地 MicroZig checkout，供生成项目引用；
- 与该 MicroZig checkout 匹配的 Zig 版本；
- 如果需要修改源 `.ioc` 文件，则需要 STM32CubeMX。

从当前仓库安装：

```sh
python -m pip install -e .
```

只运行源码：

```sh
python -m pip install -r requirements.txt
python ioc2microzig.py --help
```

## 快速开始

从 `.ioc` 生成项目：

```sh
ioc2microzig path/to/Board.ioc -o board-microzig --force --copy-ioc
cd board-microzig
zig build
```

也可以不安装命令行入口，直接运行源码：

```sh
python ioc2microzig.py path/to/Board.ioc -o board-microzig --force --copy-ioc
```

默认输出目录来自 CubeMX 项目名。例如 `MotorTest.ioc` 会生成到 `motor-test-microzig`。

## 命令行

```text
usage: ioc2microzig [-h] [-o OUT] [--include INCLUDE] [--target TARGET]
                    [--microzig-path MICROZIG_PATH]
                    [--gpio-api {auto,data,hal,registers,pins,...}]
                    [--force] [--summary-only] [--copy-ioc]
                    ioc
```

| 参数 | 说明 |
| --- | --- |
| `ioc` | STM32CubeMX `.ioc` 文件路径。 |
| `-o, --out` | 输出项目目录，默认 `<project-name>-microzig`。 |
| `--include` | 选择要输出的引脚或外设，例如 `all`、`gpio,uart,tim`、`USART1`。 |
| `--target` | 覆盖 MicroZig target 表达式，例如 `stm32.chips.STM32F103C8`。 |
| `--microzig-path` | 写入 `build.zig.zon` 的本地 MicroZig 依赖路径。 |
| `--gpio-api` | 初始化后端，默认 `auto`。 |
| `--force` | 覆盖已有输出目录中的生成文件。 |
| `--summary-only` | 只解析并打印摘要，不写文件。 |
| `--copy-ioc` | 把源 `.ioc` 复制进生成项目。 |

后端名称：

| 后端 | 用途 |
| --- | --- |
| `auto` | 根据检测到的 MCU 系列自动选择。 |
| `data` | 只生成元数据、别名和 stub，不做硬件初始化。 |
| `hal` | 使用 MicroZig HAL，例如 `rcc.apply()`、`gpio.Pin`、`GPTimer`。 |
| `registers` | 直接写 `microzig.chip.peripherals` 寄存器。 |
| `pins` | 在目标支持时使用 `hal.pins.GlobalConfiguration`。 |

兼容旧名称：`manifest/comments -> data`，`f1-runtime -> hal`，`f4-basic -> registers`，`pins-v2 -> pins`。

## 生成项目结构

```text
board-microzig/
  build.zig
  build.zig.zon
  cubemx.ioc.json
  src/
    main.zig
    app.zig
    board.zig
    board_init.zig
    cubemx.zig
    peripherals.zig
    pin_manifest.zig
```

关键文件：

| 文件 | 作用 |
| --- | --- |
| `src/main.zig` | 先调用 `board_init.init()`，再调用 `app.run()`。 |
| `src/app.zig` | 应用入口，大部分固件逻辑从这里开始写。 |
| `src/board_init.zig` | 当前后端生成的板级初始化。 |
| `src/board.zig` | 引脚、外设、RCC、DMA、NVIC 元数据的稳定别名。 |
| `src/cubemx.zig` | 从选中的 `.ioc` 内容生成的类型化表。 |
| `src/peripherals.zig` | 每个 CubeMX component/peripheral 对应的扩展 stub。 |
| `cubemx.ioc.json` | 解析后的 CubeMX 配置 JSON 快照。 |

生成的 `main.zig` 刻意保持很小：

```zig
try board_init.init();
try app.run();
```

## 闪灯示例

以常见 STM32F103C8 / Blue Pill 为例，在 STM32CubeMX 中把 `PC13` 配置为 `GPIO_Output` 后重新生成项目。STM32F1 后端会根据 `.ioc` 初始化 GPIO，所以应用层只需要初始化时间源并在循环里翻转 LED：

```zig
const board = @import("board.zig");
const board_init = @import("board_init.zig");
// USER CODE BEGIN app.imports
const microzig = @import("microzig");
// USER CODE END app.imports

// USER CODE BEGIN app.decls
const time = microzig.hal.time;
const led = board_init.pins.pc13_gpio_output;
// USER CODE END app.decls

pub fn run() !void {
    _ = board.pins;
    _ = board_init.pins;
    _ = board_init.pwm;
    // USER CODE BEGIN app.run.setup
    time.init_timer(.TIM3);
    // USER CODE END app.run.setup

    while (true) {
        // USER CODE BEGIN app.run.loop
        led.toggle();
        time.sleep_ms(500);
        // USER CODE END app.run.loop
    }
}
```

如果你在 CubeMX 中给引脚设置了 User Label，请使用 `src/board_init.zig` 中生成的实际别名。很多 Blue Pill 板子的 `PC13` LED 是低电平点亮，视觉上的亮灭可能和逻辑电平相反。

编译和烧录：

```sh
zig build
zig objcopy -O binary zig-out/firmware/<name>.elf zig-out/firmware/<name>.bin
st-flash write zig-out/firmware/<name>.bin 0x08000000
```

也可以用 STM32CubeProgrammer、OpenOCD 或 probe-rs 烧录 ELF/BIN。

## 重新生成工作流

生成文件包含 CubeMX 风格的用户代码区：

```zig
// USER CODE BEGIN app.run.loop
// USER CODE END app.run.loop
```

使用 `--force` 重新生成时，以下文件中匹配区域内的代码会被保留：

- `src/app.zig`；
- `src/board_init.zig`；
- `src/peripherals.zig`。

标记外面的代码属于生成器管理，可能在下一次生成时被替换。不要重命名 `USER CODE BEGIN/END` 标记，除非你同步修改生成器。

## 验证

运行仓库检查：

```sh
python -m unittest discover -s tests
python -m compileall ioc2microzig
```

生成 STM32F1 fixture：

```sh
python ioc2microzig.py tests/fixtures/stm32f1_complex.ioc -o stm32f1-complex-microzig --force --copy-ioc
zig build --build-file stm32f1-complex-microzig/build.zig
```

MicroZig 构建时可能打印 `run exe regz (chips) stderr`。这只是生成寄存器数据的构建步骤名，本身不代表失败。只有 Zig 非零退出，或出现终止构建的 `error:`，才应视为构建失败。

## 路线图

- 在 MicroZig HAL 支持允许的范围内扩展 STM32F1 外设覆盖。
- 为 HAL 不完整的 STM32 系列增加更多寄存器级后端。
- 把 DMA/NVIC 从元数据保留推进到可用初始化。
- 为常见 ST-Link/OpenOCD/probe-rs 工作流生成调试配置模板。
- 增加更多真实板卡和 MCU 系列的 `.ioc` fixture。

## 贡献

欢迎贡献，尤其是：

- 真实板卡的 `.ioc` fixture；
- 特定 STM32 系列的后端修复；
- MicroZig API 兼容性更新；
- 锁定生成 Zig 输出的测试。

提交 pull request 前请运行：

```sh
python -m unittest discover -s tests
python -m compileall ioc2microzig
```

新增芯片支持时，优先在 `ioc2microzig/backends/families/` 添加 family context builder，并在 `ioc2microzig/backends/templates/` 添加 Jinja2 模板。Python 负责准备结构化数据，模板负责输出 Zig。

## 许可证

MIT。见 [LICENSE](LICENSE)。
