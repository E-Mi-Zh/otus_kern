#!/usr/bin/env python3
from .base_tester import BaseModuleTester
import time


class Stack2ModuleTester(BaseModuleTester):
    def test_stack_operations(self):
        """Stack emulation tests"""
        print("\n=== Stack Emulation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # 1. Тест базовых операций
            print("\n--- Basic Operations ---")

            test_sequence = [
                ("push 10", r"Pushed: 10"),
                ("push 20", r"Pushed: 20"),
                ("top", r"Stack top: 20"),
                ("pop", r"Popped: 20"),
                ("size", r"Stack size: 1"),
                ("clear", r"Stack cleared"),
                ("size", r"Stack size: 0"),
                ("pop", r"Stack underflow"),
                ("exit", r"Exiting command processing"),
            ]

            for cmd, pattern in test_sequence:
                self.set_parameter("cmd", cmd)
                time.sleep(0.1)
                self.assert_dmesg_contains(pattern, f"Command: {cmd}")

            # 2. Тест обработки ошибок
            print("\n--- Error Handling ---")
            self.set_parameter("cmd", "top")
            time.sleep(0.1)
            self.assert_dmesg_contains(r"Stack is empty", "Check top on empty stack")

            self.set_parameter("cmd", "invalid_cmd")
            time.sleep(0.1)
            self.assert_dmesg_contains(r"Unknown command", "Check invalid command")

        finally:
            self.unload_module()

    def run_all_tests(self):
        """Execute all stack emulation tests"""
        try:
            self.test_module_lifecycle()
            self.test_stack_operations()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            with open("dmesg_failure.log", "w") as f:
                f.write(self.get_dmesg_output())
            print("Debug info saved to dmesg_failure.log")
            return 1
