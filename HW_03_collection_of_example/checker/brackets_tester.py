#!/usr/bin/env python3
from .base_tester import BaseModuleTester


class BracketModuleTester(BaseModuleTester):
    def test_bracket_validation(self):
        """Bracket validation tests"""
        print("\n=== Bracket Validation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # 1. Valid strings
            print("\n--- Test Valid Sequences ---")
            valid_tests = [
                ("()", "Simple parentheses"),
                ("[]", "Simple brackets"),
                ("{}", "Simple curly braces"),
                ("({[]})", "Nested valid sequence"),
                ("()[]{}", "Multiple valid pairs"),
            ]

            for seq, desc in valid_tests:
                self.set_parameter("input", seq)
                self.set_parameter("cmd", "validate")
                self.assert_dmesg_contains(r"Result: VALID", f"{desc}: {seq}")

            # 2. Invalid strings
            print("\n--- Test Invalid Sequences ---")
            invalid_tests = [
                ("(", "Single opening parenthesis"),
                (")", "Single closing parenthesis"),
                ("([)]", "Incorrect nesting"),
                ("{]", "Mismatched types"),
                ("{[}", "Unclosed inner bracket"),
            ]

            for seq, desc in invalid_tests:
                self.set_parameter("input", seq)
                self.set_parameter("cmd", "validate")
                self.assert_dmesg_contains(r"Result: INVALID", f"{desc}: {seq}")

            print("\n--- Test Stack Clear ---")
            self.set_parameter("cmd", "clear")
            self.assert_dmesg_contains(r"Stack cleared", "Clear stack")

        finally:
            self.unload_module()

    def run_all_tests(self):
        """Execute all bracket validation tests"""
        try:
            self.test_module_lifecycle()
            self.test_bracket_validation()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            with open("dmesg_failure.log", "w") as f:
                f.write(self.get_dmesg_output())
            print("Debug info saved to dmesg_failure.log")
            return 1
