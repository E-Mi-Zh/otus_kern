#!/usr/bin/env python3
from .base_tester import BaseModuleTester


class BitmapModuleTester(BaseModuleTester):
    def test_bitmap_operations(self):
        """Bitmap-specific test operations"""
        print("\n=== Bitmap Operation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # Test setting bits
            print("\n--- Set Bit Operations ---")
            self.set_parameter("index", 0)
            self.set_parameter("cmd", "set")
            self.assert_dmesg_contains(r"Bit 0 set", "Set bit 0")

            self.set_parameter("index", 5)
            self.set_parameter("cmd", "set")
            self.assert_dmesg_contains(r"Bit 5 set", "Set bit 5")

            # Test print operation
            print("\n--- Print Operation ---")
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Current bitmap: 1[01]{4}1[0]+", "Verify bitmap contents [0,5 set]"
            )

            # Test test operation
            print("\n--- Test Bit Operations ---")
            self.set_parameter("index", 0)
            self.set_parameter("cmd", "test")
            self.assert_dmesg_contains(r"Bit 0 is set", "Test set bit 0")

            self.set_parameter("index", 1)
            self.set_parameter("cmd", "test")
            self.assert_dmesg_contains(r"Bit 1 is not set", "Test unset bit 1")

            # Test flip operation
            print("\n--- Flip Operation ---")
            self.set_parameter("index", 1)
            self.set_parameter("cmd", "flip")
            self.assert_dmesg_contains(r"Bit 1 flipped", "Flip bit 1")

            # Test find operations
            print("\n--- Find Operations ---")
            self.set_parameter("cmd", "find_set")
            self.assert_dmesg_contains(
                r"First set bit found at position 0", "Find first set bit"
            )

            self.set_parameter("cmd", "find_zero")
            self.assert_dmesg_contains(
                r"First zero bit found at position 2", "Find first zero bit"
            )

            # Test count operation
            print("\n--- Count Operation ---")
            self.set_parameter("cmd", "count")
            self.assert_dmesg_contains(r"Number of set bits: [23]", "Count set bits")

            # Test clear operation
            print("\n--- Clear Operation ---")
            self.set_parameter("index", 0)
            self.set_parameter("cmd", "clear")
            self.assert_dmesg_contains(r"Bit 0 cleared", "Clear bit 0")

            # Test bulk operations
            print("\n--- Bulk Operations ---")
            self.set_parameter("cmd", "set_all")
            self.assert_dmesg_contains(r"All bits set", "Set all bits")

            self.set_parameter("cmd", "clear_all")
            self.assert_dmesg_contains(r"All bits cleared", "Clear all bits")

        finally:
            self.unload_module()

    def run_all_tests(self):
        """Execute all bitmap module tests"""
        try:
            self.test_module_lifecycle()
            self.test_bitmap_operations()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            with open("dmesg_failure.log", "w") as f:
                f.write(self.get_dmesg_output())
            print("Debug info saved to dmesg_failure.log")
            return 1
