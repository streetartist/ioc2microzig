from collections import OrderedDict
from pathlib import Path
import unittest

from ioc2microzig.backends.families.stm32f1 import pin_context, render
from ioc2microzig.models import IocConfig, PinConfig


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


if __name__ == "__main__":
    unittest.main()
