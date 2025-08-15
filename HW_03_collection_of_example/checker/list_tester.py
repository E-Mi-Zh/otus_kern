#!/usr/bin/env python3
from .base_tester import BaseModuleTester


class ListModuleTester(BaseModuleTester):
    def test_list_operations(self):
        """List-specific test operations"""
        print("\n=== List Operation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # Test adding elements
            print("\n--- Add Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "add")
            self.assert_dmesg_contains(r"Added item: 10", "Add item 10")

            self.set_parameter("value", 20)
            self.set_parameter("cmd", "add")
            self.assert_dmesg_contains(r"Added item: 20", "Add item 20")

            # Test print operation
            print("\n--- Print Operation ---")
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"List contents:.*10 20", "Verify list contents [10, 20]"
            )

            # Test find operation
            print("\n--- Find Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "find")
            self.assert_dmesg_contains(
                r"Item 10 found in list", "Find existing item 10"
            )

            # Test swap operation
            print("\n--- Swap Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "swap")
            self.assert_dmesg_contains(
                r"Swapped items: 20 and 10", "Swap items 10 and 20"
            )

            # Test reverse operation
            print("\n--- Reverse Operation ---")
            self.set_parameter("cmd", "reverse")
            self.assert_dmesg_contains(r"List reversed", "Reverse list")

            # Test delete operation
            print("\n--- Delete Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "del")
            self.assert_dmesg_contains(r"Deleted item: 10", "Delete item 10")

        finally:
            self.unload_module()

    def run_all_tests(self):
        """Execute all list module tests"""
        try:
            self.test_module_lifecycle()
            self.test_list_operations()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            with open("dmesg_failure.log", "w") as f:
                f.write(self.get_dmesg_output())
            print("Debug info saved to dmesg_failure.log")
            return 1
