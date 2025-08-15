#!/usr/bin/env python3
from .base_tester import BaseModuleTester


class Bin_TreeModuleTester(BaseModuleTester):
    def test_tree_operations(self):
        """Tree-specific test operations"""
        print("\n=== Tree Operation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # Проверка начального состояния дерева
            print("\n--- Initial Tree ---")
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Tree in-order traversal: 20 30 40 50 60 70 80", "Verify initial tree"
            )

            # Тест вставки нового узла
            print("\n--- Insert Operation ---")
            self.set_parameter("value", 55)
            self.set_parameter("cmd", "insert")
            self.assert_dmesg_contains(r"Inserted node: 55", "Insert node 55")

            # Проверка дерева после вставки
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Tree in-order traversal: 20 30 40 50 55 60 70 80",
                "Verify tree after insert",
            )

            # Тест удаления узла
            print("\n--- Delete Operation ---")
            self.set_parameter("value", 30)
            self.set_parameter("cmd", "delete")
            self.assert_dmesg_contains(r"Deleted node: 30", "Delete node 30")

            # Проверка дерева после удаления
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Tree in-order traversal: 20 40 50 55 60 70 80",
                "Verify tree after delete",
            )

            # Тест поиска несуществующего узла
            print("\n--- Delete Non-existent Node ---")
            self.set_parameter("value", 100)
            self.set_parameter("cmd", "delete")
            self.assert_dmesg_contains(
                r"Node 100 not found for deletion", "Try to delete non-existent node"
            )

        finally:
            self.unload_module()

    def run_all_tests(self):
        """Execute all tree module tests"""
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
