from pathlib import Path
import unittest

from ioc2microzig.parser import parse_ioc

FIXTURES = Path(__file__).parent / "fixtures"


class ParserTests(unittest.TestCase):
    def test_cubemx_pinstate_maps_to_gpio_output_level(self):
        cfg = parse_ioc(FIXTURES / "pinstate_output.ioc")

        self.assertEqual(cfg.pins[0].label, "EPD_RST")
        self.assertEqual(cfg.pins[0].gpio_output_level, "GPIO_PIN_SET")


if __name__ == "__main__":
    unittest.main()
