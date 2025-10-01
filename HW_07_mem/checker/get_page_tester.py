#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class ExGetPageTester(BaseModuleTester):
    STATS_HEADER = (
        "| Num Pages       | Status          | Avg Time (ns)  | Total Memory (KB) |"
    )
    STATS_SEPARATOR = (
        "|-----------------|-----------------|----------------|-------------------|"
    )

    def __init__(self, module_name):
        super().__init__(module_name)
        self.default_num_pages = 1  # Default number of pages
        self.page_stats = []

    def test_parameter_access(self):
        """Test reading and writing module parameters"""
        print("\n=== Module Parameter Tests ===")
        self.clear_dmesg()
        self.load_module()

        # Test reading default parameter value
        num_pages_value = self.get_parameter("num_pages")

        if num_pages_value and num_pages_value == str(self.default_num_pages):
            self.test_count += 1
            self.passed_count += 1
            print(
                f"Test #{self.test_count}: Default num_pages value is {num_pages_value} - PASS"
            )
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Default num_pages value check - FAIL")

        # Test setting parameter to one value
        test_num_pages = 2
        if self.set_parameter("num_pages", str(test_num_pages)):
            self.test_count += 1
            self.passed_count += 1
            print(f"Test #{self.test_count}: Set num_pages to {test_num_pages} - PASS")
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Set num_pages to {test_num_pages} - FAIL")

        self.unload_module()

    def test_allocation_success(self):
        """Test successful page allocation with default parameters"""
        print("\n=== Allocation Success Test ===")
        self.clear_dmesg()
        self.load_module()

        # Check for successful allocation message
        success = self.assert_dmesg_contains(
            r"get_page: SUCCESS", "Page allocation successful"
        )

        # Check for allocation details
        if success:
            self.assert_dmesg_contains(
                r"get_page: \d+ pages allocated, avg time per page: \d+ ns",
                "Allocation details with timing",
            )

        self.unload_module()

    def parse_page_stats(self, dmesg_output):
        """Parse page allocation statistics from dmesg output"""
        # Pattern for successful allocation
        success_pattern = r"get_page: SUCCESS.*get_page: (\d+) pages allocated, avg time per page: (\d+) ns"
        success_match = re.search(success_pattern, dmesg_output, re.DOTALL)

        if success_match:
            num_pages = int(success_match.group(1))
            avg_time_ns = int(success_match.group(2))
            return "SUCCESS", avg_time_ns, num_pages

        # Pattern for failed allocation
        fail_pattern = r"get_page: FAIL"
        if re.search(fail_pattern, dmesg_output):
            return "FAIL", None, None

        return "UNKNOWN", None, None

    def parse_failed_page_count(self, dmesg_output):
        """Parse the page number where allocation failed"""
        # Pattern for failed allocation with page number
        fail_pattern = r"get_page: FAIL at page (\d+)"
        fail_match = re.search(fail_pattern, dmesg_output)

        if fail_match:
            failed_at_page = int(fail_match.group(1))
            return failed_at_page

        return None

    def test_page_count_sweep(self):
        """Test different page counts"""
        print("\n=== Page Count Sweep Test ===")

        # Generate page count series: doubling until we find failure
        test_counts = []
        count = 1  # Start from 1 page
        max_count = 1024 * 1024 * 16 // 4  # Up to 4 million pages (16GB)

        while count <= max_count:
            test_counts.append(count)
            count *= 2

        self.page_stats = []  # Reset stats for this test run

        for num_pages in test_counts:
            print(f"\n--- Testing {num_pages} pages ---")
            try:
                self.clear_dmesg()
            except subprocess.CalledProcessError:
                # Ignore dmesg clearing errors, continue with test
                pass

            # Load module with parameter
            self.load_module(f"num_pages={num_pages}")

            # Parse allocation statistics from dmesg
            dmesg_output = self.get_dmesg_output()
            status, avg_time, actual_pages = self.parse_page_stats(dmesg_output)
            failed_at_page = (
                self.parse_failed_page_count(dmesg_output) if status == "FAIL" else None
            )

            # Calculate total memory (assuming 4KB per page)
            page_size_kb = 4  # Standard page size is 4KB
            if status == "SUCCESS":
                total_memory_kb = num_pages * page_size_kb
            elif status == "FAIL" and failed_at_page is not None:
                total_memory_kb = failed_at_page * page_size_kb
            else:
                total_memory_kb = 0

            self.page_stats.append(
                {
                    "num_pages": num_pages,
                    "status": status,
                    "avg_time_ns": avg_time,
                    "total_memory_kb": total_memory_kb,
                    "failed_at_page": failed_at_page,
                }
            )

            print(f"Allocation result: {status}")
            if avg_time:
                print(f"Average allocation time: {avg_time} ns")
                print(f"Total memory: {total_memory_kb} KB")

            if status == "FAIL" and failed_at_page is not None:
                print(f"Failed at page: {failed_at_page}")

            # Stop testing if we hit failure
            if status == "FAIL":
                print(f"Stopping page count sweep at {num_pages} pages due to failure")
                self.unload_module()
                break

            self.unload_module()

        # Print page count statistics table
        self.print_page_stats()

    def test_module_messages(self):
        """Test module initialization and exit messages"""
        print("\n=== Module Message Tests ===")
        self.clear_dmesg()

        # Test loading message
        self.load_module()
        self.assert_dmesg_contains(
            rf"\[INIT\] {self.module_name} module loaded", "Module load message"
        )

        # Test unloading message
        self.unload_module()
        self.assert_dmesg_contains(
            rf"\[EXIT\] {self.module_name} module unloaded", "Module unload message"
        )

    def print_page_stats(self):
        """Print page count statistics in table format"""
        if not self.page_stats:
            print("\nNo page count statistics collected")
            return

        print("\n=== Page Count Statistics ===")
        print(self.STATS_HEADER)
        print(self.STATS_SEPARATOR)

        total_time_per_kb = 0
        successful_allocations = 0

        for stat in self.page_stats:
            num_pages = stat["num_pages"]
            status = stat["status"]
            avg_time = stat["avg_time_ns"]
            total_memory_kb = stat["total_memory_kb"]

            # Format the columns
            time_str = f"{avg_time:>15}" if avg_time is not None else " " * 15
            status_str = f"{status:>15}"
            memory_str = f"{total_memory_kb:>18}" if total_memory_kb else " " * 18

            print(f"| {num_pages:>15} | {status_str} | {time_str} | {memory_str} |")

            # Calculate average time per KB for successful allocations
            if status == "SUCCESS" and avg_time is not None and total_memory_kb > 0:
                time_per_kb = avg_time / total_memory_kb
                total_time_per_kb += time_per_kb
                successful_allocations += 1

        # Print average time per KB
        if successful_allocations > 0:
            print(
                f"\nAverage allocation time per KB: {int(total_time_per_kb / successful_allocations)} ns"
            )

    def run_all_tests(self):
        """Run all tests for ex_get_page module"""
        print(f"=== Testing {self.module_name} module ===\n")

        try:
            # Run various test suites
            self.test_module_lifecycle()
            self.test_parameter_access()
            self.test_allocation_success()
            self.test_page_count_sweep()

            # Print final summary
            return self.print_summary()

        except Exception as e:
            print(f"\n[!] Error during testing: {e}")
            self.failed_count += 1
            return self.print_summary()
