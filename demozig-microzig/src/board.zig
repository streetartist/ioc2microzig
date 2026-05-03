pub const cubemx = @import("cubemx.zig");

pub const chip = cubemx.chip;
pub const raw_ioc = cubemx.raw_ioc;
pub const dma = cubemx.dma_table;
pub const nvic = cubemx.nvic_table;
pub const rcc = cubemx.rcc_config;

pub const pins = struct {
    pub const pa13_sys_jtms_swdio = cubemx.pin(0); // PA13: SYS_JTMS-SWDIO
    pub const pa14_sys_jtck_swclk = cubemx.pin(1); // PA14: SYS_JTCK-SWCLK
    pub const pc13_gpio_output = cubemx.pin(2); // PC13: GPIO_Output
    pub const pc14_rcc_osc32_in = cubemx.pin(3); // PC14: RCC_OSC32_IN
    pub const pc15_rcc_osc32_out = cubemx.pin(4); // PC15: RCC_OSC32_OUT
    pub const pd0_rcc_osc_in = cubemx.pin(5); // PD0: RCC_OSC_IN
    pub const pd1_rcc_osc_out = cubemx.pin(6); // PD1: RCC_OSC_OUT
    pub const vp_sys_vs_systick_sys_vs_systick = cubemx.pin(7); // VP_SYS_VS_Systick: SYS_VS_Systick
};

pub const peripherals = struct {
    pub const gpio = cubemx.component(0); // GPIO
    pub const nvic = cubemx.component(1); // NVIC
    pub const rcc = cubemx.component(2); // RCC
    pub const sys = cubemx.component(3); // SYS
};

pub fn pin(comptime name_or_label: []const u8) ?cubemx.Pin {
    return cubemx.findPin(name_or_label);
}

pub fn peripheral(comptime name: []const u8) ?cubemx.Component {
    return cubemx.findComponent(name);
}
