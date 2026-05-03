const board = @import("board.zig");
const cubemx = @import("cubemx.zig");
// USER CODE BEGIN peripherals.imports
// USER CODE END peripherals.imports

// USER CODE BEGIN peripherals.decls
// USER CODE END peripherals.decls

pub fn initAll() !void {
    try initClocks();
    try initGpioDefaults();
    try initDma();
    try initNvic();
    try initGpio();
    try initComponentNvic();
    try initRcc();
    try initSys();
    // USER CODE BEGIN peripherals.initAll
    // USER CODE END peripherals.initAll
}

pub fn initClocks() !void {
    _ = board.rcc;
    // RCC entries are preserved in board.rcc and cubemx.rcc_config.
    // Keep this function as the single place where you port the CubeMX clock tree
    // to the MicroZig HAL for your STM32 family.
    // USER CODE BEGIN peripherals.initClocks
    // USER CODE END peripherals.initClocks
}

pub fn initGpioDefaults() !void {
    _ = board.pins;
    // Pin direction/pull/speed/default-level metadata is in cubemx.pin_table.
    // Use board.pins.<alias> from application code and program GPIO here when
    // the exact MicroZig GPIO API for your chip family is selected.
    // USER CODE BEGIN peripherals.initGpioDefaults
    // USER CODE END peripherals.initGpioDefaults
}

pub fn initDma() !void {
    _ = board.dma;
    // DMA requests are preserved in board.dma and cubemx.dmaConfig(...).
    // USER CODE BEGIN peripherals.initDma
    // USER CODE END peripherals.initDma
}

pub fn initNvic() !void {
    _ = board.nvic;
    // NVIC priorities/enables are preserved in board.nvic.
    // USER CODE BEGIN peripherals.initNvic
    // USER CODE END peripherals.initNvic
}

pub fn initGpio() !void {
    const self = board.peripherals.gpio;
    _ = self;
    // CubeMX component: GPIO (GPIO)
    // Pins:
    // - PC13  GPIO_Output 
    // Config:
    // - groupedBy = 
    // USER CODE BEGIN peripherals.initGpio
    // USER CODE END peripherals.initGpio
    // TODO: Replace this stub with family-specific MicroZig HAL setup.
}

pub fn initComponentNvic() !void {
    const self = board.peripherals.nvic;
    _ = self;
    // CubeMX component: NVIC (NVIC)
    // Pins:
    // - No pins mapped to this component in the selected output.
    // Config:
    // - BusFault_IRQn = true\:0\:0\:false\:false\:true\:false\:false\:false
    // - DebugMonitor_IRQn = true\:0\:0\:false\:false\:true\:false\:false\:false
    // - ForceEnableDMAVector = true
    // - HardFault_IRQn = true\:0\:0\:false\:false\:true\:false\:false\:false
    // - MemoryManagement_IRQn = true\:0\:0\:false\:false\:true\:false\:false\:false
    // - NonMaskableInt_IRQn = true\:0\:0\:false\:false\:true\:false\:false\:false
    // - PendSV_IRQn = true\:0\:0\:false\:false\:true\:false\:false\:false
    // - PriorityGroup = NVIC_PRIORITYGROUP_4
    // - SVCall_IRQn = true\:0\:0\:false\:false\:true\:false\:false\:false
    // - SysTick_IRQn = true\:15\:0\:false\:false\:true\:false\:true\:false
    // - UsageFault_IRQn = true\:0\:0\:false\:false\:true\:false\:false\:false
    // USER CODE BEGIN peripherals.initComponentNvic
    // USER CODE END peripherals.initComponentNvic
    // TODO: Replace this stub with family-specific MicroZig HAL setup.
}

pub fn initRcc() !void {
    const self = board.peripherals.rcc;
    _ = self;
    // CubeMX component: RCC (RCC)
    // Pins:
    // - PC14  RCC_OSC32_IN 
    // - PC15  RCC_OSC32_OUT 
    // - PD0   RCC_OSC_IN 
    // - PD1   RCC_OSC_OUT 
    // Config:
    // - ADCFreqValue = 36000000
    // - AHBFreq_Value = 72000000
    // - APB1CLKDivider = RCC_HCLK_DIV2
    // - APB1Freq_Value = 36000000
    // - APB1TimFreq_Value = 72000000
    // - APB2Freq_Value = 72000000
    // - APB2TimFreq_Value = 72000000
    // - FCLKCortexFreq_Value = 72000000
    // - FamilyName = M
    // - HCLKFreq_Value = 72000000
    // - IPParameters = ADCFreqValue,AHBFreq_Value,APB1CLKDivider,APB1Freq_Value,APB1TimFreq_Value,APB2Freq_Value,APB2TimFreq_Value,FCLKCortexFreq_Value,FamilyName,HCLKFreq_Value,MCOFreq_Value,PLLCLKFreq_Value,PLLMCOFreq_Value,PLLMUL,PLLSourceVirtual,SYSCLKFreq_VALUE,SYSCLKSource,TimSysFreq_Value,USBFreq_Value,VCOOutput2Freq_Value
    // - MCOFreq_Value = 72000000
    // - PLLCLKFreq_Value = 72000000
    // - PLLMCOFreq_Value = 36000000
    // - PLLMUL = RCC_PLL_MUL9
    // - PLLSourceVirtual = RCC_PLLSOURCE_HSE
    // - SYSCLKFreq_VALUE = 72000000
    // - SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK
    // - TimSysFreq_Value = 72000000
    // - USBFreq_Value = 72000000
    // - ... 1 more entries are in cubemx.componentConfig(self)
    // USER CODE BEGIN peripherals.initRcc
    // USER CODE END peripherals.initRcc
    // TODO: Replace this stub with family-specific MicroZig HAL setup.
}

pub fn initSys() !void {
    const self = board.peripherals.sys;
    _ = self;
    // CubeMX component: SYS (SYS)
    // Pins:
    // - PA13  SYS_JTMS-SWDIO 
    // - PA14  SYS_JTCK-SWCLK 
    // - VP_SYS_VS_Systick SYS_VS_Systick 
    // Config:
    // - No component-specific CubeMX config entries.
    // USER CODE BEGIN peripherals.initSys
    // USER CODE END peripherals.initSys
    // TODO: Replace this stub with family-specific MicroZig HAL setup.
}

