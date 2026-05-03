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
