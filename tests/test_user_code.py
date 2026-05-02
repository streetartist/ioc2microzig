import unittest

from ioc2microzig.user_code import extract_user_regions, merge_user_regions


class UserCodeTests(unittest.TestCase):
    def test_extract_user_regions(self):
        text = """\
// USER CODE BEGIN app.decls
const x = 1;
// USER CODE END app.decls
"""
        self.assertEqual(extract_user_regions(text), {"app.decls": "\nconst x = 1;\n"})


    def test_merge_user_regions_preserves_matching_region(self):
        old = """\
// USER CODE BEGIN app.run.loop
led.toggle();
// USER CODE END app.run.loop
"""
        new = """\
// USER CODE BEGIN app.run.loop
asm volatile ("nop");
// USER CODE END app.run.loop
"""

        merged, missing = merge_user_regions(new, old)

        self.assertEqual(missing, [])
        self.assertIn("led.toggle();", merged)
        self.assertNotIn("asm volatile", merged)


if __name__ == "__main__":
    unittest.main()
