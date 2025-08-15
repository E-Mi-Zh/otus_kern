#!/usr/bin/env python3
from .base_tester import BaseModuleTester
import random
import re


class BSearchModuleTester(BaseModuleTester):
    def test_bsearch_operations(self):
        """Binary search specific test operations"""
        print("\n=== Binary Search Operation Tests ===")
        saved_values = []  # For saved values for search test
        self.clear_dmesg()
        self.load_module()

        try:
            # Initialize array
            print("\n--- Initialize Array ---")
            self.set_parameter("cmd", "init")
            self.assert_dmesg_contains(
                r"Initialized array with 100 random elements",
                "Initialize array with random values",
            )

            # Test print unsorted array
            print("\n--- Print Unsorted Array ---")
            self.set_parameter("cmd", "print")
            dmesg_output = self.get_dmesg_output()

            # Saving values for search
            values_line = re.search(
                r"Current array \(\d+ elements\):(.*)", dmesg_output
            )
            if values_line:
                saved_values = [
                    int(v) for v in values_line.group(1).split() if v.strip()
                ]
                print(f"Saved array values: {saved_values[:10]}...")  # first 10 values
            self.assert_dmesg_contains(
                r"Current array \(100 elements\):", "Print unsorted array"
            )
            self.assert_dmesg_contains(
                r"Array is NOT sorted", "Verify array is not sorted"
            )

            # Test sort operation
            print("\n--- Sort Operation ---")
            self.set_parameter("cmd", "sort")
            self.assert_dmesg_contains(r"Array sorted", "Sort array")

            # Verify array after sort
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(r"Array is sorted", "Verify array is sorted")

            # Test search with random existing value
            print("\n--- Search Existing Value ---")
            if not saved_values:
                print("Warning: No values saved from array printout")
                return

            # Get random value from saved
            test_value = random.choice(saved_values)
            self.set_parameter("value", test_value)
            self.set_parameter("cmd", "search")
            self.assert_dmesg_contains(
                f"Value {test_value} found in array",
                f"Search existing value {test_value}",
            )

            # Test search with non-existing value
            print("\n--- Search Non-existing Value ---")
            self.set_parameter("value", 100)  # 100 is outside 0-99 range
            self.set_parameter("cmd", "search")
            self.assert_dmesg_contains(
                r"Value 100 not found in array", "Search non-existing value 100"
            )

            # Verify array remains unchanged after searches
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Array is sorted", "Verify array remains sorted after searches"
            )

        finally:
            self.unload_module()

    def run_all_tests(self):
        """Execute all binary search module tests"""
        try:
            self.test_module_lifecycle()
            self.test_bsearch_operations()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            with open("dmesg_failure.log", "w") as f:
                f.write(self.get_dmesg_output())
            print("Debug info saved to dmesg_failure.log")
            return 1
