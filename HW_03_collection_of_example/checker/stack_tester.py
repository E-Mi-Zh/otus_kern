#!/usr/bin/env python3
from .base_tester import BaseModuleTester


class StackModuleTester(BaseModuleTester):
    def test_stack_operations(self):
        """Stack-specific test operations"""
        print("\n=== Stack Operation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # 1. Проверка пустого стека
            print("\n--- Test Empty Stack ---")
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Stack is empty", "Verify stack is initially empty"
            )

            # 2. Тест push операций
            print("\n--- Test Push Operations ---")
            push_values = [10, 20, 30, 40]
            for val in push_values:
                self.set_parameter("value", val)
                self.set_parameter("cmd", "push")
                self.assert_dmesg_contains(f"Pushed: {val}", f"Push value {val}")

            # 3. Проверка содержимого стека (LIFO порядок)
            print("\n--- Verify Stack Contents ---")
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Stack contents \(top to bottom\): 40 30 20 10",
                "Verify stack contents after pushes",
            )

            # 4. Тест pop операций
            print("\n--- Test Pop Operations ---")
            for expected_val in reversed(push_values):
                self.set_parameter("cmd", "pop")
                self.assert_dmesg_contains(
                    f"Popped: {expected_val}", f"Pop value (expect {expected_val})"
                )

            # 5. Проверка underflow
            print("\n--- Test Stack Underflow ---")
            self.set_parameter("cmd", "pop")
            self.assert_dmesg_contains(
                r"Stack underflow", "Verify pop from empty stack"
            )

            # 6. Тест clear операции
            print("\n--- Test Clear Operation ---")
            # Сначала снова добавим элементы
            for val in [50, 60]:
                self.set_parameter("value", val)
                self.set_parameter("cmd", "push")

            self.set_parameter("cmd", "clear")
            self.assert_dmesg_contains(r"Stack cleared", "Verify stack clear")

            # Проверка что стек пуст после очистки
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Stack is empty", "Verify stack empty after clear"
            )

        finally:
            self.unload_module()

    def run_all_tests(self):
        """Execute all stack module tests"""
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
