import zlib
import unittest

from ioc2microzig.render import package_fingerprint, render_app_zig, render_build_zig


class RenderTests(unittest.TestCase):
    def test_package_fingerprint_high_bits_match_zig_name_crc32(self):
        name = "demozig"

        fingerprint = package_fingerprint(name)

        self.assertEqual(fingerprint >> 32, zlib.crc32(name.encode("utf-8")) & 0xFFFFFFFF)
        self.assertNotEqual(fingerprint & 0xFFFFFFFF, 0)

    def test_build_zig_has_user_regions(self):
        text = render_build_zig("Demo", "example.target")

        for name in ["build.imports", "build.options", "build.firmware", "build.decls"]:
            self.assertIn(f"// USER CODE BEGIN {name}", text)
            self.assertIn(f"// USER CODE END {name}", text)

    def test_app_zig_has_callback_and_helper_user_regions(self):
        text = render_app_zig([])

        for name in ["app.helpers", "app.callbacks"]:
            self.assertIn(f"// USER CODE BEGIN {name}", text)
            self.assertIn(f"// USER CODE END {name}", text)


if __name__ == "__main__":
    unittest.main()
