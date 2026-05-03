import zlib
import unittest

from ioc2microzig.render import package_fingerprint


class RenderTests(unittest.TestCase):
    def test_package_fingerprint_high_bits_match_zig_name_crc32(self):
        name = "demozig"

        fingerprint = package_fingerprint(name)

        self.assertEqual(fingerprint >> 32, zlib.crc32(name.encode("utf-8")) & 0xFFFFFFFF)
        self.assertNotEqual(fingerprint & 0xFFFFFFFF, 0)


if __name__ == "__main__":
    unittest.main()
