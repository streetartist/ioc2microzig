const microzig = @import("microzig");
const stm32 = microzig.hal;
const generated = @import("peripherals.zig");
// USER CODE BEGIN board_init.imports
// USER CODE END board_init.imports

// USER CODE BEGIN board_init.decls
// USER CODE END board_init.decls

pub fn init() !void {
    try initClocks();
    initGpio();
    initTimers();
    initSpis();
    try initI2cs();
    initAdcs();
    try initUarts();
    try generated.initAll();
    // USER CODE BEGIN board_init.init
    // USER CODE END board_init.init
}

const rcc = stm32.rcc;
const gpio = stm32.gpio;
const GPTimer = stm32.timer.GPTimer;

pub const pins = struct {
    pub const pc13_gpio_output = gpio.Pin.from_port(.C, 13);
};

// No generated timer aliases.
// No generated UART aliases.
// No generated I2C aliases.
// No generated SPI aliases.
// No generated ADC aliases.

pub const pwm = struct {
    // No generated PWM outputs.
};

fn initClocks() !void {
    _ = try rcc.apply(.{
        .SYSCLKSource = .RCC_SYSCLKSOURCE_PLLCLK,
        .PLLSource = .RCC_PLLSOURCE_HSE,
        .PLLMUL = .RCC_PLL_MUL9,
        .APB1CLKDivider = .RCC_HCLK_DIV2,
        .flags = .{
            .HSEOscillator = true,
        },
    });
    rcc.enable_clock(.GPIOA);
    rcc.enable_clock(.GPIOC);
    rcc.enable_clock(.GPIOD);
    // CubeMX RCC summary:
    // RCC.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK
    // RCC.PLLSourceVirtual = RCC_PLLSOURCE_HSE
    // RCC.APB1CLKDivider = RCC_HCLK_DIV2
    // RCC.FCLKCortexFreq_Value = 72000000
    // RCC.HCLKFreq_Value = 72000000
    // RCC.PLLCLKFreq_Value = 72000000
    // RCC.PLLMCOFreq_Value = 36000000
    // RCC.PLLMUL = RCC_PLL_MUL9
    // RCC.SYSCLKFreq_VALUE = 72000000
    // USER CODE BEGIN board_init.initClocks
    // USER CODE END board_init.initClocks
}

fn initGpio() void {
    // STM32F1 MicroZig GPIO setup generated from CubeMX pins.
    pins.pc13_gpio_output.put(0);
    pins.pc13_gpio_output.set_output_mode(.general_purpose_push_pull, .max_2MHz); // PC13: GPIO_Output
    // USER CODE BEGIN board_init.initGpio
    // USER CODE END board_init.initGpio
}

fn initTimers() void {
    // STM32F1 MicroZig timer setup generated from CubeMX TIM components.
    // No timer setup inferred.
    // USER CODE BEGIN board_init.initTimers
    // USER CODE END board_init.initTimers
}

fn initSpis() void {
    // STM32F1 MicroZig SPI setup generated from CubeMX SPI components.
    // No SPI setup inferred.
    // USER CODE BEGIN board_init.initSpis
    // USER CODE END board_init.initSpis
}

fn initI2cs() !void {
    // STM32F1 MicroZig I2C setup generated from CubeMX I2C components.
    // No I2C setup inferred.
    // USER CODE BEGIN board_init.initI2cs
    // USER CODE END board_init.initI2cs
}

fn initAdcs() void {
    // STM32F1 ADC aliases and analog GPIO setup are generated here.
    // ADC enable/calibration uses microzig.hal.time.sleep_us(); initialize a
    // time source first, then call <adc>.enable() from application USER CODE.
    // No ADC setup inferred.
    // USER CODE BEGIN board_init.initAdcs
    // USER CODE END board_init.initAdcs
}

fn initUarts() !void {
    // STM32F1 MicroZig UART setup generated from CubeMX USART/UART components.
    // No UART setup inferred.
    // USER CODE BEGIN board_init.initUarts
    // USER CODE END board_init.initUarts
}
