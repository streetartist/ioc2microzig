const std = @import("std");

pub const GpioConfig = struct {
    mode: []const u8,
    pull: []const u8,
    speed: []const u8,
    output_type: []const u8,
    output_level: []const u8,
};

pub const Pin = struct {
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
};

pub const Component = struct {
    name: []const u8,
    kind: []const u8,
    pin_start: usize,
    pin_count: usize,
    config_start: usize,
    config_count: usize,
};

pub const NvicIrq = struct {
    irq: []const u8,
    enabled: bool,
    preempt_priority: ?i32,
    sub_priority: ?i32,
    raw: []const u8,
};

pub const DmaRequest = struct {
    index: usize,
    request: []const u8,
    channel: []const u8,
    direction: []const u8,
    priority: []const u8,
    config_start: usize,
    config_count: usize,
};

pub const KeyValue = struct {
    key: []const u8,
    value: []const u8,
};

pub const chip = struct {
    pub const cubemx_name = "STM32F103C(8-B)Tx";
    pub const cpn = "STM32F103C8T6";
    pub const family = "STM32F1";
    pub const package = "LQFP48";
    pub const project = "demozig";
};

pub const pin_table = [_]Pin{
    .{ .name = "PA13", .ioc_key = "PA13", .is_virtual = false, .port = 'A', .number = 13, .signal = "SYS_JTMS-SWDIO", .label = "", .peripheral = "SYS", .locked = false, .gpio = .{ .mode = "Serial_Wire", .pull = "", .speed = "", .output_type = "", .output_level = "" } },
    .{ .name = "PA14", .ioc_key = "PA14", .is_virtual = false, .port = 'A', .number = 14, .signal = "SYS_JTCK-SWCLK", .label = "", .peripheral = "SYS", .locked = false, .gpio = .{ .mode = "Serial_Wire", .pull = "", .speed = "", .output_type = "", .output_level = "" } },
    .{ .name = "PC13", .ioc_key = "PC13-TAMPER-RTC", .is_virtual = false, .port = 'C', .number = 13, .signal = "GPIO_Output", .label = "", .peripheral = "GPIO", .locked = true, .gpio = .{ .mode = "", .pull = "", .speed = "", .output_type = "", .output_level = "" } },
    .{ .name = "PC14", .ioc_key = "PC14-OSC32_IN", .is_virtual = false, .port = 'C', .number = 14, .signal = "RCC_OSC32_IN", .label = "", .peripheral = "RCC", .locked = false, .gpio = .{ .mode = "LSE-External-Oscillator", .pull = "", .speed = "", .output_type = "", .output_level = "" } },
    .{ .name = "PC15", .ioc_key = "PC15-OSC32_OUT", .is_virtual = false, .port = 'C', .number = 15, .signal = "RCC_OSC32_OUT", .label = "", .peripheral = "RCC", .locked = false, .gpio = .{ .mode = "LSE-External-Oscillator", .pull = "", .speed = "", .output_type = "", .output_level = "" } },
    .{ .name = "PD0", .ioc_key = "PD0-OSC_IN", .is_virtual = false, .port = 'D', .number = 0, .signal = "RCC_OSC_IN", .label = "", .peripheral = "RCC", .locked = false, .gpio = .{ .mode = "HSE-External-Oscillator", .pull = "", .speed = "", .output_type = "", .output_level = "" } },
    .{ .name = "PD1", .ioc_key = "PD1-OSC_OUT", .is_virtual = false, .port = 'D', .number = 1, .signal = "RCC_OSC_OUT", .label = "", .peripheral = "RCC", .locked = false, .gpio = .{ .mode = "HSE-External-Oscillator", .pull = "", .speed = "", .output_type = "", .output_level = "" } },
    .{ .name = "VP_SYS_VS_Systick", .ioc_key = "VP_SYS_VS_Systick", .is_virtual = true, .port = null, .number = null, .signal = "SYS_VS_Systick", .label = "", .peripheral = "SYS", .locked = false, .gpio = .{ .mode = "SysTick", .pull = "", .speed = "", .output_type = "", .output_level = "" } },
};

pub const component_table = [_]Component{
    .{ .name = "GPIO", .kind = "GPIO", .pin_start = 0, .pin_count = 1, .config_start = 0, .config_count = 1 },
    .{ .name = "NVIC", .kind = "NVIC", .pin_start = 1, .pin_count = 0, .config_start = 1, .config_count = 11 },
    .{ .name = "RCC", .kind = "RCC", .pin_start = 1, .pin_count = 4, .config_start = 12, .config_count = 21 },
    .{ .name = "SYS", .kind = "SYS", .pin_start = 5, .pin_count = 3, .config_start = 33, .config_count = 0 },
};

pub const component_pin_indices = [_]usize{
    2,
    3,
    4,
    5,
    6,
    0,
    1,
    7,
};

pub const component_config = [_]KeyValue{
    .{ .key = "GPIO.groupedBy", .value = "" },
    .{ .key = "NVIC.BusFault_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.DebugMonitor_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.ForceEnableDMAVector", .value = "true" },
    .{ .key = "NVIC.HardFault_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.MemoryManagement_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.NonMaskableInt_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.PendSV_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.PriorityGroup", .value = "NVIC_PRIORITYGROUP_4" },
    .{ .key = "NVIC.SVCall_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.SysTick_IRQn", .value = "true\\:15\\:0\\:false\\:false\\:true\\:false\\:true\\:false" },
    .{ .key = "NVIC.UsageFault_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "RCC.ADCFreqValue", .value = "36000000" },
    .{ .key = "RCC.AHBFreq_Value", .value = "72000000" },
    .{ .key = "RCC.APB1CLKDivider", .value = "RCC_HCLK_DIV2" },
    .{ .key = "RCC.APB1Freq_Value", .value = "36000000" },
    .{ .key = "RCC.APB1TimFreq_Value", .value = "72000000" },
    .{ .key = "RCC.APB2Freq_Value", .value = "72000000" },
    .{ .key = "RCC.APB2TimFreq_Value", .value = "72000000" },
    .{ .key = "RCC.FCLKCortexFreq_Value", .value = "72000000" },
    .{ .key = "RCC.FamilyName", .value = "M" },
    .{ .key = "RCC.HCLKFreq_Value", .value = "72000000" },
    .{ .key = "RCC.IPParameters", .value = "ADCFreqValue,AHBFreq_Value,APB1CLKDivider,APB1Freq_Value,APB1TimFreq_Value,APB2Freq_Value,APB2TimFreq_Value,FCLKCortexFreq_Value,FamilyName,HCLKFreq_Value,MCOFreq_Value,PLLCLKFreq_Value,PLLMCOFreq_Value,PLLMUL,PLLSourceVirtual,SYSCLKFreq_VALUE,SYSCLKSource,TimSysFreq_Value,USBFreq_Value,VCOOutput2Freq_Value" },
    .{ .key = "RCC.MCOFreq_Value", .value = "72000000" },
    .{ .key = "RCC.PLLCLKFreq_Value", .value = "72000000" },
    .{ .key = "RCC.PLLMCOFreq_Value", .value = "36000000" },
    .{ .key = "RCC.PLLMUL", .value = "RCC_PLL_MUL9" },
    .{ .key = "RCC.PLLSourceVirtual", .value = "RCC_PLLSOURCE_HSE" },
    .{ .key = "RCC.SYSCLKFreq_VALUE", .value = "72000000" },
    .{ .key = "RCC.SYSCLKSource", .value = "RCC_SYSCLKSOURCE_PLLCLK" },
    .{ .key = "RCC.TimSysFreq_Value", .value = "72000000" },
    .{ .key = "RCC.USBFreq_Value", .value = "72000000" },
    .{ .key = "RCC.VCOOutput2Freq_Value", .value = "8000000" },
};

pub const rcc_config = [_]KeyValue{
    .{ .key = "ADCFreqValue", .value = "36000000" },
    .{ .key = "AHBFreq_Value", .value = "72000000" },
    .{ .key = "APB1CLKDivider", .value = "RCC_HCLK_DIV2" },
    .{ .key = "APB1Freq_Value", .value = "36000000" },
    .{ .key = "APB1TimFreq_Value", .value = "72000000" },
    .{ .key = "APB2Freq_Value", .value = "72000000" },
    .{ .key = "APB2TimFreq_Value", .value = "72000000" },
    .{ .key = "FCLKCortexFreq_Value", .value = "72000000" },
    .{ .key = "FamilyName", .value = "M" },
    .{ .key = "HCLKFreq_Value", .value = "72000000" },
    .{ .key = "IPParameters", .value = "ADCFreqValue,AHBFreq_Value,APB1CLKDivider,APB1Freq_Value,APB1TimFreq_Value,APB2Freq_Value,APB2TimFreq_Value,FCLKCortexFreq_Value,FamilyName,HCLKFreq_Value,MCOFreq_Value,PLLCLKFreq_Value,PLLMCOFreq_Value,PLLMUL,PLLSourceVirtual,SYSCLKFreq_VALUE,SYSCLKSource,TimSysFreq_Value,USBFreq_Value,VCOOutput2Freq_Value" },
    .{ .key = "MCOFreq_Value", .value = "72000000" },
    .{ .key = "PLLCLKFreq_Value", .value = "72000000" },
    .{ .key = "PLLMCOFreq_Value", .value = "36000000" },
    .{ .key = "PLLMUL", .value = "RCC_PLL_MUL9" },
    .{ .key = "PLLSourceVirtual", .value = "RCC_PLLSOURCE_HSE" },
    .{ .key = "SYSCLKFreq_VALUE", .value = "72000000" },
    .{ .key = "SYSCLKSource", .value = "RCC_SYSCLKSOURCE_PLLCLK" },
    .{ .key = "TimSysFreq_Value", .value = "72000000" },
    .{ .key = "USBFreq_Value", .value = "72000000" },
    .{ .key = "VCOOutput2Freq_Value", .value = "8000000" },
};

pub const nvic_table = [_]NvicIrq{
    .{ .irq = "BusFault_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .irq = "DebugMonitor_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .irq = "ForceEnableDMAVector", .enabled = true, .preempt_priority = null, .sub_priority = null, .raw = "true" },
    .{ .irq = "HardFault_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .irq = "MemoryManagement_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .irq = "NonMaskableInt_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .irq = "PendSV_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .irq = "SVCall_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .irq = "SysTick_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:15\\:0\\:false\\:false\\:true\\:false\\:true\\:false" },
    .{ .irq = "UsageFault_IRQn", .enabled = false, .preempt_priority = null, .sub_priority = null, .raw = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
};

pub const dma_table = [_]DmaRequest{
    // No indexed DMA requests found.
};

pub const dma_config = [_]KeyValue{
    // No DMA config entries found.
};

pub const raw_ioc = [_]KeyValue{
    .{ .key = "CAD.formats", .value = "" },
    .{ .key = "CAD.pinconfig", .value = "" },
    .{ .key = "CAD.provider", .value = "" },
    .{ .key = "File.Version", .value = "6" },
    .{ .key = "GPIO.groupedBy", .value = "" },
    .{ .key = "KeepUserPlacement", .value = "false" },
    .{ .key = "Mcu.CPN", .value = "STM32F103C8T6" },
    .{ .key = "Mcu.Family", .value = "STM32F1" },
    .{ .key = "Mcu.IP0", .value = "NVIC" },
    .{ .key = "Mcu.IP1", .value = "RCC" },
    .{ .key = "Mcu.IP2", .value = "SYS" },
    .{ .key = "Mcu.IPNb", .value = "3" },
    .{ .key = "Mcu.Name", .value = "STM32F103C(8-B)Tx" },
    .{ .key = "Mcu.Package", .value = "LQFP48" },
    .{ .key = "Mcu.Pin0", .value = "PC13-TAMPER-RTC" },
    .{ .key = "Mcu.Pin1", .value = "PC14-OSC32_IN" },
    .{ .key = "Mcu.Pin2", .value = "PC15-OSC32_OUT" },
    .{ .key = "Mcu.Pin3", .value = "PD0-OSC_IN" },
    .{ .key = "Mcu.Pin4", .value = "PD1-OSC_OUT" },
    .{ .key = "Mcu.Pin5", .value = "PA13" },
    .{ .key = "Mcu.Pin6", .value = "PA14" },
    .{ .key = "Mcu.Pin7", .value = "VP_SYS_VS_Systick" },
    .{ .key = "Mcu.PinsNb", .value = "8" },
    .{ .key = "Mcu.ThirdPartyNb", .value = "0" },
    .{ .key = "Mcu.UserConstants", .value = "" },
    .{ .key = "Mcu.UserName", .value = "STM32F103C8Tx" },
    .{ .key = "MxCube.Version", .value = "6.17.0" },
    .{ .key = "MxDb.Version", .value = "DB.6.0.170" },
    .{ .key = "NVIC.BusFault_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.DebugMonitor_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.ForceEnableDMAVector", .value = "true" },
    .{ .key = "NVIC.HardFault_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.MemoryManagement_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.NonMaskableInt_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.PendSV_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.PriorityGroup", .value = "NVIC_PRIORITYGROUP_4" },
    .{ .key = "NVIC.SVCall_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "NVIC.SysTick_IRQn", .value = "true\\:15\\:0\\:false\\:false\\:true\\:false\\:true\\:false" },
    .{ .key = "NVIC.UsageFault_IRQn", .value = "true\\:0\\:0\\:false\\:false\\:true\\:false\\:false\\:false" },
    .{ .key = "PA13.Mode", .value = "Serial_Wire" },
    .{ .key = "PA13.Signal", .value = "SYS_JTMS-SWDIO" },
    .{ .key = "PA14.Mode", .value = "Serial_Wire" },
    .{ .key = "PA14.Signal", .value = "SYS_JTCK-SWCLK" },
    .{ .key = "PC13-TAMPER-RTC.Locked", .value = "true" },
    .{ .key = "PC13-TAMPER-RTC.Signal", .value = "GPIO_Output" },
    .{ .key = "PC14-OSC32_IN.Mode", .value = "LSE-External-Oscillator" },
    .{ .key = "PC14-OSC32_IN.Signal", .value = "RCC_OSC32_IN" },
    .{ .key = "PC15-OSC32_OUT.Mode", .value = "LSE-External-Oscillator" },
    .{ .key = "PC15-OSC32_OUT.Signal", .value = "RCC_OSC32_OUT" },
    .{ .key = "PCC.Checker", .value = "false" },
    .{ .key = "PCC.Display", .value = "Plot\\: All Steps" },
    .{ .key = "PCC.Line", .value = "STM32F103" },
    .{ .key = "PCC.MCU", .value = "STM32F103C(8-B)Tx" },
    .{ .key = "PCC.PartNumber", .value = "STM32F103C8Tx" },
    .{ .key = "PCC.Series", .value = "STM32F1" },
    .{ .key = "PCC.Temperature", .value = "25" },
    .{ .key = "PCC.Vdd", .value = "3.3" },
    .{ .key = "PD0-OSC_IN.Mode", .value = "HSE-External-Oscillator" },
    .{ .key = "PD0-OSC_IN.Signal", .value = "RCC_OSC_IN" },
    .{ .key = "PD1-OSC_OUT.Mode", .value = "HSE-External-Oscillator" },
    .{ .key = "PD1-OSC_OUT.Signal", .value = "RCC_OSC_OUT" },
    .{ .key = "PinOutPanel.RotationAngle", .value = "0" },
    .{ .key = "ProjectManager.AskForMigrate", .value = "true" },
    .{ .key = "ProjectManager.BackupPrevious", .value = "false" },
    .{ .key = "ProjectManager.CompilerLinker", .value = "GCC" },
    .{ .key = "ProjectManager.CompilerOptimize", .value = "6" },
    .{ .key = "ProjectManager.ComputerToolchain", .value = "false" },
    .{ .key = "ProjectManager.CoupleFile", .value = "false" },
    .{ .key = "ProjectManager.CustomerFirmwarePackage", .value = "" },
    .{ .key = "ProjectManager.DefaultFWLocation", .value = "true" },
    .{ .key = "ProjectManager.DeletePrevious", .value = "true" },
    .{ .key = "ProjectManager.DeviceId", .value = "STM32F103C8Tx" },
    .{ .key = "ProjectManager.FirmwarePackage", .value = "STM32Cube FW_F1 V1.8.7" },
    .{ .key = "ProjectManager.FreePins", .value = "false" },
    .{ .key = "ProjectManager.FreePinsContext", .value = "" },
    .{ .key = "ProjectManager.HalAssertFull", .value = "false" },
    .{ .key = "ProjectManager.HeapSize", .value = "0x200" },
    .{ .key = "ProjectManager.KeepUserCode", .value = "true" },
    .{ .key = "ProjectManager.LastFirmware", .value = "true" },
    .{ .key = "ProjectManager.LibraryCopy", .value = "1" },
    .{ .key = "ProjectManager.MainLocation", .value = "Core/Src" },
    .{ .key = "ProjectManager.NoMain", .value = "false" },
    .{ .key = "ProjectManager.PreviousToolchain", .value = "" },
    .{ .key = "ProjectManager.ProjectBuild", .value = "false" },
    .{ .key = "ProjectManager.ProjectFileName", .value = "demozig.ioc" },
    .{ .key = "ProjectManager.ProjectName", .value = "demozig" },
    .{ .key = "ProjectManager.ProjectStructure", .value = "" },
    .{ .key = "ProjectManager.RegisterCallBack", .value = "" },
    .{ .key = "ProjectManager.StackSize", .value = "0x400" },
    .{ .key = "ProjectManager.TargetToolchain", .value = "CMake" },
    .{ .key = "ProjectManager.ToolChainLocation", .value = "" },
    .{ .key = "ProjectManager.UAScriptAfterPath", .value = "" },
    .{ .key = "ProjectManager.UAScriptBeforePath", .value = "" },
    .{ .key = "ProjectManager.UnderRoot", .value = "false" },
    .{ .key = "ProjectManager.functionlistsort", .value = "1-SystemClock_Config-RCC-false-HAL-false,2-MX_GPIO_Init-GPIO-false-HAL-true" },
    .{ .key = "RCC.ADCFreqValue", .value = "36000000" },
    .{ .key = "RCC.AHBFreq_Value", .value = "72000000" },
    .{ .key = "RCC.APB1CLKDivider", .value = "RCC_HCLK_DIV2" },
    .{ .key = "RCC.APB1Freq_Value", .value = "36000000" },
    .{ .key = "RCC.APB1TimFreq_Value", .value = "72000000" },
    .{ .key = "RCC.APB2Freq_Value", .value = "72000000" },
    .{ .key = "RCC.APB2TimFreq_Value", .value = "72000000" },
    .{ .key = "RCC.FCLKCortexFreq_Value", .value = "72000000" },
    .{ .key = "RCC.FamilyName", .value = "M" },
    .{ .key = "RCC.HCLKFreq_Value", .value = "72000000" },
    .{ .key = "RCC.IPParameters", .value = "ADCFreqValue,AHBFreq_Value,APB1CLKDivider,APB1Freq_Value,APB1TimFreq_Value,APB2Freq_Value,APB2TimFreq_Value,FCLKCortexFreq_Value,FamilyName,HCLKFreq_Value,MCOFreq_Value,PLLCLKFreq_Value,PLLMCOFreq_Value,PLLMUL,PLLSourceVirtual,SYSCLKFreq_VALUE,SYSCLKSource,TimSysFreq_Value,USBFreq_Value,VCOOutput2Freq_Value" },
    .{ .key = "RCC.MCOFreq_Value", .value = "72000000" },
    .{ .key = "RCC.PLLCLKFreq_Value", .value = "72000000" },
    .{ .key = "RCC.PLLMCOFreq_Value", .value = "36000000" },
    .{ .key = "RCC.PLLMUL", .value = "RCC_PLL_MUL9" },
    .{ .key = "RCC.PLLSourceVirtual", .value = "RCC_PLLSOURCE_HSE" },
    .{ .key = "RCC.SYSCLKFreq_VALUE", .value = "72000000" },
    .{ .key = "RCC.SYSCLKSource", .value = "RCC_SYSCLKSOURCE_PLLCLK" },
    .{ .key = "RCC.TimSysFreq_Value", .value = "72000000" },
    .{ .key = "RCC.USBFreq_Value", .value = "72000000" },
    .{ .key = "RCC.VCOOutput2Freq_Value", .value = "8000000" },
    .{ .key = "VP_SYS_VS_Systick.Mode", .value = "SysTick" },
    .{ .key = "VP_SYS_VS_Systick.Signal", .value = "SYS_VS_Systick" },
    .{ .key = "board", .value = "custom" },
};

pub fn pin(comptime index: usize) Pin {
    return pin_table[index];
}

pub fn component(comptime index: usize) Component {
    return component_table[index];
}

pub fn componentPins(comptime c: Component) []const usize {
    return component_pin_indices[c.pin_start .. c.pin_start + c.pin_count];
}

pub fn componentConfig(comptime c: Component) []const KeyValue {
    return component_config[c.config_start .. c.config_start + c.config_count];
}

pub fn dmaConfig(comptime d: DmaRequest) []const KeyValue {
    return dma_config[d.config_start .. d.config_start + d.config_count];
}

pub fn findPin(comptime name_or_label: []const u8) ?Pin {
    inline for (pin_table) |p| {
        if (std.mem.eql(u8, p.name, name_or_label) or
            std.mem.eql(u8, p.ioc_key, name_or_label) or
            std.mem.eql(u8, p.label, name_or_label))
        {
            return p;
        }
    }
    return null;
}

pub fn findComponent(comptime name: []const u8) ?Component {
    inline for (component_table) |c| {
        if (std.mem.eql(u8, c.name, name)) return c;
    }
    return null;
}
