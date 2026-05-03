from collections import OrderedDict
from pathlib import Path
import unittest

from ioc2microzig.backends.families.stm32f1 import pin_context, render
from ioc2microzig.models import ComponentConfig, IocConfig, PinConfig


def component(name, config):
    return ComponentConfig(name=name, kind=name.rstrip("0123456789"), config=config, pin_indices=())


class Stm32F1BackendTests(unittest.TestCase):
    def test_gpio_output_defaults_match_cubemx_f1_low_speed_reset(self):
        pin = PinConfig(
            index=0,
            ioc_key="PC13-TAMPER-RTC",
            name="PC13",
            is_virtual=False,
            port="C",
            number=13,
            signal="GPIO_Output",
        )

        ctx = pin_context("pc13_gpio_output", pin)

        self.assertEqual(ctx["setup"]["kind"], "output")
        self.assertEqual(ctx["setup"]["mode"], "general_purpose_push_pull")
        self.assertEqual(ctx["setup"]["speed"], "max_2MHz")
        self.assertEqual(ctx["setup"]["initial"], "0")

    def test_gpio_output_reset_level_is_not_misread_as_set(self):
        pin = PinConfig(
            index=0,
            ioc_key="PC13-TAMPER-RTC",
            name="PC13",
            is_virtual=False,
            port="C",
            number=13,
            signal="GPIO_Output",
            gpio_output_level="GPIO_PIN_RESET",
        )

        ctx = pin_context("pc13_gpio_output", pin)

        self.assertEqual(ctx["setup"]["initial"], "0")

    def test_gpio_output_open_drain_and_set_level(self):
        pin = PinConfig(
            index=0,
            ioc_key="PB7",
            name="PB7",
            is_virtual=False,
            port="B",
            number=7,
            signal="GPIO_Output",
            gpio_output_type="GPIO_MODE_OUTPUT_OD",
            gpio_speed="GPIO_SPEED_FREQ_HIGH",
            gpio_output_level="GPIO_PIN_SET",
        )

        ctx = pin_context("pb7", pin)

        self.assertEqual(ctx["setup"]["mode"], "general_purpose_open_drain")
        self.assertEqual(ctx["setup"]["speed"], "max_50MHz")
        self.assertEqual(ctx["setup"]["initial"], "1")

    def test_alternate_function_output_has_no_initial_gpio_write(self):
        pin = PinConfig(
            index=0,
            ioc_key="PA9",
            name="PA9",
            is_virtual=False,
            port="A",
            number=9,
            signal="USART1_TX",
        )

        ctx = pin_context("pa9_usart1_tx", pin)

        self.assertEqual(ctx["setup"]["kind"], "output")
        self.assertEqual(ctx["setup"]["mode"], "alternate_function_push_pull")
        self.assertNotIn("initial", ctx["setup"])

    def test_render_clocks_sys_rcc_ports_but_only_configures_gpio_pins(self):
        pins = [
            PinConfig(0, "PA13", "PA13", False, "A", 13, signal="SYS_JTMS-SWDIO", gpio_mode="Serial_Wire"),
            PinConfig(1, "PC13-TAMPER-RTC", "PC13", False, "C", 13, signal="GPIO_Output"),
            PinConfig(2, "PD0-OSC_IN", "PD0", False, "D", 0, signal="RCC_OSC_IN", gpio_mode="HSE-External-Oscillator"),
        ]
        cfg = IocConfig(
            path=Path("demo.ioc"),
            raw=OrderedDict(),
            entries=[],
            project_name="demo",
            mcu_name="STM32F103C8Tx",
            mcu_cpn="STM32F103C8T6",
            mcu_family="STM32F1",
            package="LQFP48",
            ip_names=[],
            pins=pins,
            components=[],
            rcc={},
            nvic=[],
            nvic_raw={},
            dma=[],
            dma_raw={},
        )

        output = render(cfg, pins)

        self.assertIn("rcc.enable_clock(.GPIOA);", output)
        self.assertIn("rcc.enable_clock(.GPIOC);", output)
        self.assertIn("rcc.enable_clock(.GPIOD);", output)
        self.assertIn("pub const pc13_gpio_output = gpio.Pin.from_port(.C, 13);", output)
        self.assertIn("pins.pc13_gpio_output.set_output_mode(.general_purpose_push_pull, .max_2MHz);", output)
        self.assertNotIn("pa13_sys_jtms_swdio = gpio.Pin", output)
        self.assertNotIn("pd0_rcc_osc_in = gpio.Pin", output)

    def test_render_spi_i2c_adc_uart_pwm_context(self):
        pins = [
            PinConfig(0, "PA0-WKUP", "PA0", False, "A", 0, signal="ADC1_IN0"),
            PinConfig(1, "PA1", "PA1", False, "A", 1, signal="TIM2_CH2"),
            PinConfig(2, "PA5", "PA5", False, "A", 5, signal="SPI1_SCK"),
            PinConfig(3, "PA6", "PA6", False, "A", 6, signal="SPI1_MISO"),
            PinConfig(4, "PA7", "PA7", False, "A", 7, signal="SPI1_MOSI"),
            PinConfig(5, "PA9", "PA9", False, "A", 9, signal="USART1_TX"),
            PinConfig(6, "PA10", "PA10", False, "A", 10, signal="USART1_RX"),
            PinConfig(7, "PB6", "PB6", False, "B", 6, signal="I2C1_SCL"),
            PinConfig(8, "PB7", "PB7", False, "B", 7, signal="I2C1_SDA"),
        ]
        cfg = IocConfig(
            path=Path("demo.ioc"),
            raw=OrderedDict(),
            entries=[],
            project_name="demo",
            mcu_name="STM32F103C8Tx",
            mcu_cpn="STM32F103C8T6",
            mcu_family="STM32F1",
            package="LQFP48",
            ip_names=[],
            pins=pins,
            components=[
                component("ADC1", {"Channel-0#ChannelRegularConversion": "ADC_CHANNEL_0"}),
                component("DAC1", {}),
                component("I2C1", {"I2C_Speed_Mode": "I2C_Fast"}),
                component("SPI1", {
                    "BaudRatePrescaler": "SPI_BAUDRATEPRESCALER_8",
                    "CLKPhase": "SPI_PHASE_2EDGE",
                    "CLKPolarity": "SPI_POLARITY_HIGH",
                    "DataSize": "SPI_DATASIZE_16BIT",
                }),
                component("TIM2", {
                    "Channel-PWM Generation2 CH2": "TIM_CHANNEL_2",
                    "Period": "1000",
                    "Prescaler": "72-1",
                    "PulseNoDither_2": "250",
                }),
                component("USART1", {"BaudRate": "115200"}),
            ],
            rcc={},
            nvic=[],
            nvic_raw={},
            dma=[],
            dma_raw={},
        )

        output = render(cfg, pins)

        self.assertIn("rcc.enable_clock(.ADC1);", output)
        self.assertIn("TODO DAC1:", output)
        self.assertIn("rcc.enable_clock(.I2C1);", output)
        self.assertIn("rcc.enable_clock(.SPI1);", output)
        self.assertIn("rcc.enable_clock(.TIM2);", output)
        self.assertIn("rcc.enable_clock(.USART1);", output)
        self.assertIn("pins.pa0_adc1_in0.set_input_mode(.analog);", output)
        self.assertIn("pins.pb6_i2c1_scl.set_output_mode(.alternate_function_open_drain, .max_50MHz);", output)
        self.assertIn("try i2c1.runtime_apply(.{", output)
        self.assertIn(".speed = 400000,", output)
        self.assertIn("spi1.apply(.{", output)
        self.assertIn(".phase = .SecondEdge,", output)
        self.assertIn(".polarity = .IdleHigh,", output)
        self.assertIn(".data_size = .Bits16,", output)
        self.assertIn(".prescaler = .Div8,", output)
        self.assertIn("tim2_pwm.set_duty(1, 250);", output)
        self.assertIn("try usart1.apply_runtime(.{", output)


if __name__ == "__main__":
    unittest.main()
