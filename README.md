# ioc2microzig

把 STM32CubeMX 的 `.ioc` 文件转换成 MicroZig 项目骨架，并尽量生成可用的初始化代码。

## 安装

```sh
python -m pip install -e .
```

如果只想直接运行源码，也可以安装依赖后使用 `python ioc2microzig.py`：

```sh
python -m pip install -r requirements.txt
```

## 基本用法

```sh
ioc2microzig MotorTest.ioc --force
```

源码方式：

```sh
python ioc2microzig.py MotorTest.ioc --force
```

默认输出目录来自 CubeMX 项目名，例如 `MotorTest` 会生成到：

```text
motor-test-microzig
```

指定输出目录：

```sh
python ioc2microzig.py MotorTest.ioc -o my-board --force
```

## 生成后端

`--gpio-api` 现在使用更直观的后端名：

- `auto`：自动选择合适后端，默认值。
- `data`：只生成 CubeMX 数据、别名和 stub，不做真实硬件初始化。
- `hal`：使用 MicroZig 高层 HAL API，例如 `rcc.apply()`、`gpio.Pin`、`GPTimer`。
- `registers`：直接写 `microzig.chip.peripherals` 寄存器，适合没有完整 HAL 的 chip target。
- `pins`：使用 `hal.pins.GlobalConfiguration`。

兼容旧名字：`manifest/comments -> data`，`f1-runtime -> hal`，`f4-basic -> registers`，`pins-v2 -> pins`。

## 当前覆盖

- STM32F1：`auto -> hal`
  - RCC：从 CubeMX RCC 字段生成 `rcc.apply(...)`
  - GPIO：生成输入、输出、复用输出、I2C 开漏等配置
  - TIM PWM：生成 `GPTimer.init(.TIMx).into_pwm_mode()`、周期、预分频、通道启用
  - USART/UART：生成基础 `apply_runtime(...)`

- STM32F4/F40x/F41x/F42x/F43x：`auto -> registers`
  - GPIO：直接写 RCC GPIO 时钟、MODER、AFR
  - RCC/TIM/UART：目前保留 TODO 和 CubeMX 摘要，后续可扩展

- 其他系列：`auto -> pins`
  - GPIO：优先生成 `hal.pins.GlobalConfiguration`
  - UART：尝试生成 UART v3 初始化
  - 不支持项保留 TODO

## 代码结构

```text
ioc2microzig.py
requirements.txt
ioc2microzig/
  backends/         # 芯片/系列后端、后端注册、模板
    board_init.py   # 根据 --gpio-api / auto 分发到具体 family
    common.py       # 后端共享的小工具
    registry.py     # 后端注册、别名、auto 选择逻辑
    families/
      data.py
      generic_pins.py
      stm32f1.py
      stm32f4.py
    templates/
      data/board_init.zig.j2
      generic/pins_board_init.zig.j2
      stm32f1/board_init.zig.j2
      stm32f4/board_init.zig.j2
  cli.py            # 命令行参数
  parser.py         # 解析 .ioc
  models.py         # 数据模型
  render.py         # 生成通用项目文件；初始化后端不放这里
  templating.py     # Jinja2 模板加载
  user_code.py      # USER CODE 区域提取和重新生成合并
```

## 继续开发：新增芯片适配

建议按“后端 + 模板”的方式扩展，不要继续在 Python 里拼大段 Zig 字符串。

### 1. 判断用哪个层级

先看 MicroZig 对目标芯片暴露了什么：

```sh
rg "pub const .* = @import|pub fn apply|GlobalConfiguration|Uart|GPTimer" D:\ioc2microzig\microzig\port\stmicro\stm32\src\hals
```

选择原则：

- 有稳定 `microzig.hal` 且 API 足够：用 `hal`
- 没有 HAL，但 `microzig.chip.peripherals` 可用：用 `registers`
- 有 `hal.pins.GlobalConfiguration`：用 `pins`
- 不确定或只想保存信息：用 `data`

### 2. 新增或修改模板

模板放在后端目录里：

```text
ioc2microzig/backends/templates/
```

例如新增 G0 寄存器后端：

```text
ioc2microzig/backends/templates/stm32g0/board_init.zig.j2
```

模板负责输出 Zig。Python family 文件只准备结构化变量，不要拼整行 Zig 代码，例如：

- `pins`
- `gpio_ports`
- `peripheral_clocks`
- `timers`
- `pwm_outputs`
- `uarts`
- `rcc_comments`

### 3. 在 `backends/registry.py` 注册后端

增加一项：

```python
BACKENDS["g0-registers"] = InitBackend(
    name="g0-registers",
    description="STM32G0 register-level init",
    template="stm32g0/board_init.zig.j2",
)
```

如果要让 CLI 直接可选，也把名字加入 `CLI_BACKEND_CHOICES`。

如果只是 `auto` 内部使用，也要在 `select_auto_backend()` 里加规则：

```python
if chip.startswith("STM32G0"):
    return "g0-registers"
```

### 4. 在 `backends/families/` 增加 family 文件

新增文件：

```text
ioc2microzig/backends/families/stm32g0.py
```

模式参考 `stm32f1.py` / `stm32f4.py`：Python 只做 `.ioc` 到上下文的转换，最后调用模板。

```python
def render(cfg, pins) -> str:
    return render_template(
        BACKENDS["g0-registers"].template,
        pins=[...],
        timers=[...],
        uarts=[...],
        rcc_comments=...,
    )
```

然后在 `backends/board_init.py` 里分发：

```python
if gpio_api == "g0-registers":
    return stm32g0.render(cfg, pins)
```

### 5. 尽量转换哪些内容

按优先级做：

1. RCC：系统时钟源、PLL、AHB/APB 分频、外设时钟 enable
2. GPIO：input/output/analog/alternate/open-drain/pull/speed
3. TIM PWM：prescaler、period、channel、polarity、enable
4. UART/USART：TX/RX 引脚、baud、word length、stop bits、parity
5. SPI/I2C/ADC/DMA/NVIC：先生成可编译初始化，再逐步补完整参数

无法确定的配置不要丢掉，生成 TODO，并保留 `cubemx.zig` / `cubemx.ioc.json` 中的原始信息。

### 6. 验证

Python 语法：

```sh
python -m compileall ioc2microzig
```

生成当前测试项目：

```sh
python ioc2microzig.py MotorTest.ioc --force
cd motor-test-microzig
zig build
```

强制指定后端测试：

```sh
python ioc2microzig.py MotorTest.ioc -o test-data --gpio-api data --force
python ioc2microzig.py MotorTest.ioc -o test-hal --gpio-api hal --force
```

临时测试其他芯片 target：

```sh
python ioc2microzig.py MotorTest.ioc ^
  -o D:\tmp\motor-f407 ^
  --target stm32.chips.STM32F407VE ^
  --gpio-api registers ^
  --microzig-path ../../ioc2microzig/microzig ^
  --force
```

然后：

```sh
cd D:\tmp\motor-f407
zig build
```

## 重新生成时保留用户代码

生成器会在 `src/app.zig`、`src/board_init.zig`、`src/peripherals.zig` 里输出 CubeMX 风格的用户代码区：

```zig
// USER CODE BEGIN app.run.loop
// USER CODE END app.run.loop
```

重新执行 `python ioc2microzig.py MotorTest.ioc --force` 时，只有这些 `BEGIN/END` 中间的内容会被保留。标记外面的代码属于生成器管理，下一次生成会被覆盖。

常用位置：

- `src/app.zig`：写业务逻辑，例如主循环、状态机、控制算法。
- `src/board_init.zig`：补充当前后端还没完全转换的初始化，例如特殊 RCC、GPIO、TIM、UART 参数。
- `src/peripherals.zig`：按外设补初始化，例如 `peripherals.initTim2`、`peripherals.initUsart1`。

不要改动 `USER CODE BEGIN ...` 和 `USER CODE END ...` 这两行本身；区域名必须保持一致，生成器才能把旧内容合并回新文件。

## 从生成代码到点灯

下面用最常见的 STM32F103C8 / Blue Pill 举例，让板载 LED 闪烁起来。很多 Blue Pill 板子的 LED 接在 `PC13`。如果你的板子不是 `PC13`，看本节最后的“换成其他引脚”。

### 1. 在 CubeMX 里配置 LED 引脚

如果你的 `.ioc` 还没有 LED 引脚，先在 STM32CubeMX 里做这几步：

1. 选择 `PC13`。
2. 设置为 `GPIO_Output`。
3. 可选：把 User Label 设置成 `led`。
4. 保存 `.ioc`。

如果你用的板子 LED 在 `PA5`、`PB0` 等其他引脚，就配置对应引脚为 `GPIO_Output`。

### 2. 生成 MicroZig 项目

在 `D:\ioc2microzig` 下执行：

```sh
python ioc2microzig.py MotorTest.ioc --force
cd motor-test-microzig
```

先确认生成项目能编译：

```sh
zig build
```

### 3. 修改 `src/app.zig`

不要整文件替换，只把代码写进 `USER CODE` 区域。生成后的 `src/app.zig` 大致如下，把点灯代码加到对应位置：

```zig
const board = @import("board.zig");
// USER CODE BEGIN app.imports
const microzig = @import("microzig");
// USER CODE END app.imports

// USER CODE BEGIN app.decls
const stm32 = microzig.hal;
const rcc = stm32.rcc;
const gpio = stm32.gpio;
const time = stm32.time;

const led = gpio.Pin.from_port(.C, 13);
// USER CODE END app.decls

pub fn run() !void {
    _ = board.pins; // 这行是生成器给的提示，保留或删除都可以。
    // USER CODE BEGIN app.run.setup
    rcc.enable_clock(.GPIOC);
    time.init_timer(.TIM3);

    led.set_output_mode(.general_purpose_push_pull, .max_2MHz);
    // USER CODE END app.run.setup

    while (true) {
        // USER CODE BEGIN app.run.loop
        led.toggle();
        time.sleep_ms(500);
        // USER CODE END app.run.loop
    }
}
```

这段代码做了四件事：

- 打开 `GPIOC` 时钟。
- 用 `TIM3` 初始化 MicroZig 的毫秒延时。
- 把 `PC13` 配成推挽输出。
- 每 500 ms 翻转一次 LED。

注意：`src/main.zig` 会先调用生成的 `board_init.init()`，再调用 `app.run()`。所以 CubeMX 里已经配置的 RCC/GPIO/TIM/PWM 初始化仍然会先执行；这里的代码只是一个最小点灯例子。以后重新生成项目时，上面写在 `USER CODE` 区域里的代码会被保留。

### 4. 编译

```sh
zig build
```

固件输出：

```text
zig-out\firmware\motor_test.elf
```

### 5. 生成 BIN 并烧录

如果你的烧录工具支持 ELF，可以直接烧录 `motor_test.elf`。如果需要 BIN：

```sh
zig objcopy -O binary zig-out\firmware\motor_test.elf zig-out\firmware\motor_test.bin
```

使用 ST-Link 和 `st-flash` 时通常是：

```sh
st-flash write zig-out\firmware\motor_test.bin 0x08000000
```

也可以用 STM32CubeProgrammer、OpenOCD 或 probe-rs 烧录 ELF/BIN。

### 换成其他引脚

如果 LED 在 `PA5`，改这两处：

```zig
const led = gpio.Pin.from_port(.A, 5);

pub fn run() !void {
    rcc.enable_clock(.GPIOA);
    // 其他代码不变
}
```

如果 LED 在 `PB0`：

```zig
const led = gpio.Pin.from_port(.B, 0);

pub fn run() !void {
    rcc.enable_clock(.GPIOB);
    // 其他代码不变
}
```

端口字母和引脚号要和 CubeMX 里设置的 GPIO 输出引脚一致。
