#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class ExMempoolTester(BaseModuleTester):
    STATS_HEADER_SIZE = "| Element Size (kb) | Status          | Avg Time (ns)  |"
    STATS_SEPARATOR_SIZE = "|-------------------|-----------------|----------------|"
    STATS_HEADER_POOL = (
        "| Pool Size         | Status          | Avg Time (ns)  | Total Memory    |"
    )
    STATS_SEPARATOR_POOL = (
        "|-------------------|-----------------|----------------|----------------|"
    )

    def __init__(self, module_name):
        super().__init__(module_name)
        self.default_element_size = 1  # Default element size in KB
        self.default_pool_size = 1  # Default pool size
        self.size_stats = []
        self.pool_stats = []
        self.max_successful_size = None

    def test_parameter_access(self):
        """Test reading and writing module parameters"""
        print("\n=== Module Parameter Tests ===")
        self.clear_dmesg()
        self.load_module()

        # Test reading default parameter values
        element_size_value = self.get_parameter("element_size_kb")
        pool_size_value = self.get_parameter("pool_size")

        if element_size_value and element_size_value == str(self.default_element_size):
            self.test_count += 1
            self.passed_count += 1
            print(
                f"Test #{self.test_count}: Default element_size_kb value is {element_size_value} - PASS"
            )
        else:
            self.test_count += 1
            self.failed_count += 1
            print(
                f"Test #{self.test_count}: Default element_size_kb value check - FAIL"
            )

        if pool_size_value and pool_size_value == str(self.default_pool_size):
            self.test_count += 1
            self.passed_count += 1
            print(
                f"Test #{self.test_count}: Default pool_size value is {pool_size_value} - PASS"
            )
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Default pool_size value check - FAIL")

        # Test setting parameters to one value each
        test_element_size = 2
        test_pool_size = 2

        if self.set_parameter("element_size_kb", str(test_element_size)):
            self.test_count += 1
            self.passed_count += 1
            print(
                f"Test #{self.test_count}: Set element_size_kb to {test_element_size} KB - PASS"
            )
        else:
            self.test_count += 1
            self.failed_count += 1
            print(
                f"Test #{self.test_count}: Set element_size_kb to {test_element_size} KB - FAIL"
            )

        if self.set_parameter("pool_size", str(test_pool_size)):
            self.test_count += 1
            self.passed_count += 1
            print(f"Test #{self.test_count}: Set pool_size to {test_pool_size} - PASS")
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Set pool_size to {test_pool_size} - FAIL")

        self.unload_module()

    def test_allocation_success(self):
        """Test successful pool allocation with default parameters"""
        print("\n=== Allocation Success Test ===")
        self.clear_dmesg()
        self.load_module()

        # Check for successful pool creation message
        success = self.assert_dmesg_contains(
            r"mempool: SUCCESS - pool created", "Pool creation successful"
        )

        # Check for allocation details
        if success:
            self.assert_dmesg_contains(
                r"mempool: \d+ elements allocated, avg time per element: \d+ ns",
                "Allocation details with timing",
            )

        self.unload_module()

    def parse_pool_stats(self, dmesg_output):
        """Parse pool allocation statistics from dmesg output"""
        # Pattern for successful pool creation and allocation
        success_pattern = r"mempool: SUCCESS - pool created.*mempool: (\d+) elements allocated, avg time per element: (\d+) ns"
        success_match = re.search(success_pattern, dmesg_output, re.DOTALL)

        if success_match:
            pool_size = int(success_match.group(1))
            avg_time_ns = int(success_match.group(2))
            return "SUCCESS", avg_time_ns, pool_size

        # Pattern for failed allocation
        fail_pattern = r"mempool: FAIL"
        if re.search(fail_pattern, dmesg_output):
            return "FAIL", None, None

        return "UNKNOWN", None, None

    def parse_failed_element_count(self, dmesg_output):
        """Parse the element number where allocation failed"""
        # Pattern for failed allocation with element number
        fail_pattern = r"mempool: FAIL at element (\d+)"
        fail_match = re.search(fail_pattern, dmesg_output)

        if fail_match:
            failed_at_element = int(fail_match.group(1))
            return failed_at_element

        return None

    def test_element_size_sweep(self):
        """Test different element sizes with pool_size=1"""
        print("\n=== Element Size Sweep Test (pool_size=1) ===")

        # Generate size series: doubling until we find failure
        test_sizes = []
        size = 1  # Start from 1 KB
        max_size = 1024 * 1024  # Up to 1024 MB

        while size <= max_size:
            test_sizes.append(size)
            size *= 2

        self.size_stats = []  # Reset stats for this test run

        for size in test_sizes:
            print(f"\n--- Testing element size: {size} KB (pool_size=1) ---")
            self.clear_dmesg()
            # Load module with parameters
            self.load_module(f"element_size_kb={size} pool_size=1")

            # Parse allocation statistics from dmesg
            dmesg_output = self.get_dmesg_output()
            status, avg_time, pool_size = self.parse_pool_stats(dmesg_output)

            self.size_stats.append(
                {
                    "element_size_kb": size,
                    "status": status,
                    "avg_time_ns": avg_time,
                    "pool_size": pool_size,
                }
            )

            print(f"Pool creation result: {status}")
            if avg_time:
                print(f"Average allocation time: {avg_time} ns")

            # Track the maximum successful size
            if status == "SUCCESS":
                self.max_successful_size = size

            # Stop testing if we hit failure (assuming larger sizes will also fail)
            if status == "FAIL":
                print(f"Stopping size sweep at {size} KB due to failure")
                self.unload_module()
                break

            self.unload_module()

        # Print size statistics table
        self.print_size_stats()

    def test_pool_size_sweep(self):
        """Test different pool sizes with max successful element size"""
        if self.max_successful_size is None:
            print("\nNo successful element size found, skipping pool size sweep")
            return

        print(
            f"\n=== Pool Size Sweep Test (element_size_kb={self.max_successful_size}) ==="
        )

        # Generate pool size series: doubling
        test_sizes = []
        size = 1  # Start from 1 element
        max_size = 1024 * 1024  # Up to 1 million elements

        while size <= max_size:
            test_sizes.append(size)
            size *= 2

        self.pool_stats = []  # Reset stats for this test run

        for pool_size in test_sizes:
            print(
                f"\n--- Testing pool size: {pool_size} (element_size_kb={self.max_successful_size}) ---"
            )
            self.clear_dmesg()
            # Load module with parameters
            self.load_module(
                f"element_size_kb={self.max_successful_size} pool_size={pool_size}"
            )

            # Parse allocation statistics from dmesg
            dmesg_output = self.get_dmesg_output()
            status, avg_time, actual_pool_size = self.parse_pool_stats(dmesg_output)
            failed_at_element = (
                self.parse_failed_element_count(dmesg_output)
                if status == "FAIL"
                else None
            )

            total_memory = (
                self.max_successful_size * pool_size if status == "SUCCESS" else 0
            )

            self.pool_stats.append(
                {
                    "pool_size": pool_size,
                    "status": status,
                    "avg_time_ns": avg_time,
                    "total_memory_kb": total_memory,
                    "failed_at_element": failed_at_element,
                }
            )

            print(f"Allocation result: {status}")
            if avg_time:
                print(f"Average allocation time: {avg_time} ns")
                print(f"Total memory: {total_memory} KB")

            if status == "FAIL" and failed_at_element is not None:
                print(f"Failed at element: {failed_at_element}")

            # Stop testing if we hit failure
            if status == "FAIL":
                print(
                    f"Stopping pool size sweep at {pool_size} elements due to failure"
                )
                self.unload_module()
                break

            self.unload_module()

        # Print pool size statistics table
        self.print_pool_stats()

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

    def print_size_stats(self):
        """Print element size statistics in table format"""
        if not self.size_stats:
            print("\nNo element size statistics collected")
            return

        print("\n=== Element Size Statistics ===")
        print(self.STATS_HEADER_SIZE)
        print(self.STATS_SEPARATOR_SIZE)

        total_time_per_kb = 0
        successful_sizes = 0

        for stat in self.size_stats:
            size = stat["element_size_kb"]
            status = stat["status"]
            avg_time = stat["avg_time_ns"]

            # Format the time column
            time_str = f"{avg_time:>15}" if avg_time is not None else " " * 15
            status_str = f"{status:>15}"

            print(f"| {size:>17} | {status_str} | {time_str} |")

            # Calculate average time per KB for successful allocations
            if status == "SUCCESS" and avg_time is not None and size > 0:
                time_per_kb = avg_time / size
                total_time_per_kb += time_per_kb
                successful_sizes += 1

        # Print average time per KB
        if successful_sizes > 0:
            print(
                f"\nAverage allocation time per KB: {int(total_time_per_kb / successful_sizes)} ns"
            )

    def print_pool_stats(self):
        """Print pool size statistics in table format"""
        if not self.pool_stats:
            print("\nNo pool size statistics collected")
            return

        print("\n=== Pool Size Statistics ===")
        print(self.STATS_HEADER_POOL)
        print(self.STATS_SEPARATOR_POOL)

        total_time_per_kb = 0
        successful_pools = 0

        for stat in self.pool_stats:
            pool_size = stat["pool_size"]
            status = stat["status"]
            avg_time = stat["avg_time_ns"]
            failed_at_element = stat["failed_at_element"]

            # Calculate total memory: successful allocations or partial allocation on failure
            if status == "SUCCESS":
                total_memory = stat["total_memory_kb"]
            elif status == "FAIL" and failed_at_element is not None:
                total_memory = self.max_successful_size * failed_at_element
            else:
                total_memory = 0

            # Format the columns
            time_str = f"{avg_time:>15}" if avg_time is not None else " " * 15
            status_str = f"{status:>15}"
            memory_str = f"{total_memory:>15}" if total_memory else " " * 15

            print(f"| {pool_size:>17} | {status_str} | {time_str} | {memory_str} |")

            # Calculate average time per KB for successful allocations
            if status == "SUCCESS" and avg_time is not None and total_memory > 0:
                time_per_kb = avg_time / total_memory
                total_time_per_kb += time_per_kb
                successful_pools += 1

        # Print average time per KB
        if successful_pools > 0:
            print(
                f"\nAverage allocation time per KB: {int(total_time_per_kb / successful_pools)} ns"
            )

    def run_all_tests(self):
        """Run all tests for ex_mempool module"""
        print(f"=== Testing {self.module_name} module ===\n")

        try:
            # Run various test suites
            self.test_module_lifecycle()
            self.test_parameter_access()
            self.test_allocation_success()
            self.test_element_size_sweep()
            self.test_pool_size_sweep()

            # Print final summary
            return self.print_summary()

        except Exception as e:
            print(f"\n[!] Error during testing: {e}")
            self.failed_count += 1
            return self.print_summary()
