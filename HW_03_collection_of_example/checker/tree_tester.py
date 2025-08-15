#!/usr/bin/env python3
from .base_tester import BaseModuleTester


class TreeModuleTester(BaseModuleTester):
    def test_tree_operations(self):
        """RB-tree specific test operations"""
        print("\n=== RB-Tree Operation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # Test insert
            print("\n--- Insert Operation ---")
            self.set_parameter("value", 50)
            self.set_parameter("cmd", "insert")
            self.assert_dmesg_contains(r"Inserted: 50", "Insert root node 50")

            self.set_parameter("value", 30)
            self.set_parameter("cmd", "insert")
            self.assert_dmesg_contains(r"Inserted: 30", "Insert left child 30")

            self.set_parameter("value", 70)
            self.set_parameter("cmd", "insert")
            self.assert_dmesg_contains(r"Inserted: 70", "Insert right child 70")

            # Test duplicate insert
            self.set_parameter("value", 50)
            self.set_parameter("cmd", "insert")
            self.assert_dmesg_contains(r"Insert failed", "Duplicate insert check")

            # Test find
            print("\n--- Find Operation ---")
            self.set_parameter("value", 30)
            self.set_parameter("cmd", "find")
            self.assert_dmesg_contains(r"Found: 30", "Find existing node")

            self.set_parameter("value", 99)
            self.set_parameter("cmd", "find")
            self.assert_dmesg_contains(r"Not found: 99", "Find non-existent node")

            # Test print
            print("\n--- Print Operation ---")
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(r"Tree contents", "Print tree structure")
            self.assert_dmesg_contains(r"50", "Verify root node in output")
            self.assert_dmesg_contains(r"red|black", "Verify color markers")

            # Test delete
            print("\n--- Delete Operation ---")
            self.set_parameter("value", 30)
            self.set_parameter("cmd", "delete")
            self.assert_dmesg_contains(r"Deleted: 30", "Delete node")

            # Verify deletion
            self.set_parameter("value", 30)
            self.set_parameter("cmd", "find")
            self.assert_dmesg_contains(r"Not found: 30", "Verify deletion")

            # Test clear
            print("\n--- Clear Operation ---")
            self.set_parameter("cmd", "clear")
            self.assert_dmesg_contains(r"Tree cleared", "Clear tree")

            # Verify empty tree
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(r"Tree is empty", "Verify empty tree")

        finally:
            self.unload_module()

    def run_all_tests(self):
        try:
            self.test_module_lifecycle()
            self.test_tree_operations()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            with open("dmesg_failure.log", "w") as f:
                f.write(self.get_dmesg_output())
            print("Debug info saved to dmesg_failure.log")
            return 1
