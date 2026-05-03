import unittest

from ioc2microzig.project import PRESERVE_USER_CODE


class ProjectTests(unittest.TestCase):
    def test_build_zig_is_regeneration_safe(self):
        self.assertIn("build.zig", PRESERVE_USER_CODE)


if __name__ == "__main__":
    unittest.main()
