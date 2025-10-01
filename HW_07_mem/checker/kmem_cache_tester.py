#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class ExKmemCacheTester(BaseModuleTester):
    STATS_HEADER_SIZE = "| Cache Size (kb) | Status          | Avg Time (ns)  |"
    STATS_SEPARATOR_SIZE = "|-----------------|-----------------|----------------|"
    STATS_HEADER_OBJS = (
        "| Num Objects     | Status          | Avg Time (ns)  | Total Memory (kb) |"
    )
    STATS_SEPARATOR_OBJS = (
        "|-----------------|-----------------|----------------|----------------|"
    )

    def __init__(self, module_name):
        super().__init__(module_name)
        self.default_cache_size = 1  # Default cache size in KB
        self.default_num_objs = 1  # Default number of objects
        self.size_stats = []
        self.object_stats = []
        self.max_successful_size = None

    def test_parameter_access(self):
        """Test reading and writing module parameters"""
        print("\n=== Module Parameter Tests ===")
        self.clear_dmesg()
        self.load_module()

        # Test reading default parameter values
        cache_size_value = self.get_parameter("cache_size_kb")
        num_objs_value = self.get_parameter("num_objs")

        if cache_size_value and cache_size_value == str(self.default_cache_size):
            self.test_count += 1
            self.passed_count += 1
            print(
                f"Test #{self.test_count}: Default cache_size_kb value is {cache_size_value} - PASS"
            )
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Default cache_size_kb value check - FAIL")

        if num_objs_value and num_objs_value == str(self.default_num_objs):
            self.test_count += 1
            self.passed_count += 1
            print(
                f"Test #{self.test_count}: Default num_objs value is {num_objs_value} - PASS"
            )
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Default num_objs value check - FAIL")

        # Test setting parameters to one value each
        test_cache_size = 2
        test_num_objs = 2

        if self.set_parameter("cache_size_kb", str(test_cache_size)):
            self.test_count += 1
            self.passed_count += 1
            print(
                f"Test #{self.test_count}: Set cache_size_kb to {test_cache_size} KB - PASS"
            )
        else:
            self.test_count += 1
            self.failed_count += 1
            print(
                f"Test #{self.test_count}: Set cache_size_kb to {test_cache_size} KB - FAIL"
            )

        if self.set_parameter("num_objs", str(test_num_objs)):
            self.test_count += 1
            self.passed_count += 1
            print(f"Test #{self.test_count}: Set num_objs to {test_num_objs} - PASS")
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Set num_objs to {test_num_objs} - FAIL")

        self.unload_module()

    def test_allocation_success(self):
        """Test successful cache allocation with default parameters"""
        print("\n=== Allocation Success Test ===")
        self.clear_dmesg()
        self.load_module()

        # Check for successful cache creation message
        success = self.assert_dmesg_contains(
            r"kmem_cache: SUCCESS - cache created", "Cache creation successful"
        )

        # Check for allocation details
        if success:
            self.assert_dmesg_contains(
                r"kmem_cache: \d+ objects allocated, avg time per object: \d+ ns",
                "Allocation details with timing",
            )

        self.unload_module()

    def parse_cache_stats(self, dmesg_output):
        """Parse cache allocation statistics from dmesg output"""
        # Pattern for successful cache creation and allocation
        success_pattern = r"kmem_cache: SUCCESS - cache created.*kmem_cache: (\d+) objects allocated, avg time per object: (\d+) ns"
        success_match = re.search(success_pattern, dmesg_output, re.DOTALL)

        if success_match:
            num_objects = int(success_match.group(1))
            avg_time_ns = int(success_match.group(2))
            return "SUCCESS", avg_time_ns, num_objects

        # Pattern for failed allocation
        fail_pattern = r"kmem_cache: FAIL"
        if re.search(fail_pattern, dmesg_output):
            return "FAIL", None, None

        return "UNKNOWN", None, None

    def parse_failed_object_count(self, dmesg_output):
        """Parse the object number where allocation failed"""
        # Pattern for failed allocation with object number
        fail_pattern = r"kmem_cache: FAIL at object (\d+)"
        fail_match = re.search(fail_pattern, dmesg_output)

        if fail_match:
            failed_at_obj = int(fail_match.group(1))
            return failed_at_obj

        return "UNKNOWN", None, None

    def test_cache_size_sweep(self):
        """Test different cache sizes with num_objs=1"""
        print("\n=== Cache Size Sweep Test (num_objs=1) ===")

        # Generate size series: doubling until we find failure
        test_sizes = []
        size = 1  # Start from 1 KB
        max_size = 1024 * 1024  # Up to 1024 MB

        while size <= max_size:
            test_sizes.append(size)
            size *= 2

        self.size_stats = []  # Reset stats for this test run

        for size in test_sizes:
            print(f"\n--- Testing cache size: {size} KB (num_objs=1) ---")
            self.clear_dmesg()
            # Load module with parameters
            self.load_module(f"cache_size_kb={size} num_objs=1")

            # Parse allocation statistics from dmesg
            dmesg_output = self.get_dmesg_output()
            status, avg_time, num_objs = self.parse_cache_stats(dmesg_output)

            self.size_stats.append(
                {
                    "cache_size_kb": size,
                    "status": status,
                    "avg_time_ns": avg_time,
                    "num_objs": num_objs,
                }
            )

            print(f"Cache creation result: {status}")
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

    def test_object_count_sweep(self):
        """Test different object counts with max successful cache size"""
        if self.max_successful_size is None:
            print("\nNo successful cache size found, skipping object count sweep")
            return

        print(
            f"\n=== Object Count Sweep Test (cache_size_kb={self.max_successful_size}) ==="
        )

        # Generate object count series: doubling
        test_counts = []
        count = 1  # Start from 1 object
        max_count = 1024 * 1024  # Up to 1 million objects

        while count <= max_count:
            test_counts.append(count)
            count *= 2

        self.object_stats = []  # Reset stats for this test run

        for num_objs in test_counts:
            print(
                f"\n--- Testing {num_objs} objects (cache_size_kb={self.max_successful_size}) ---"
            )
            self.clear_dmesg()
            # Load module with parameters
            self.load_module(
                f"cache_size_kb={self.max_successful_size} num_objs={num_objs}"
            )

            # Parse allocation statistics from dmesg
            dmesg_output = self.get_dmesg_output()
            status, avg_time, actual_objs = self.parse_cache_stats(dmesg_output)
            failed_at_obj = (
                self.parse_failed_object_count(dmesg_output)
                if status == "FAIL"
                else None
            )

            total_memory = (
                self.max_successful_size * num_objs if status == "SUCCESS" else 0
            )

            self.object_stats.append(
                {
                    "num_objs": num_objs,
                    "status": status,
                    "avg_time_ns": avg_time,
                    "total_memory_kb": total_memory,
                    "failed_at_obj": failed_at_obj,
                }
            )

            print(f"Allocation result: {status}")
            if avg_time:
                print(f"Average allocation time: {avg_time} ns")
                print(f"Total memory: {total_memory} KB")

            if status == "FAIL" and failed_at_obj is not None:
                print(f"Failed at object: {failed_at_obj}")

            # Stop testing if we hit failure
            if status == "FAIL":
                print(
                    f"Stopping object count sweep at {num_objs} objects due to failure"
                )
                self.unload_module()
                break

            self.unload_module()

        # Print object count statistics table
        self.print_object_stats()

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
        """Print cache size statistics in table format"""
        if not self.size_stats:
            print("\nNo cache size statistics collected")
            return

        print("\n=== Cache Size Statistics ===")
        print(self.STATS_HEADER_SIZE)
        print(self.STATS_SEPARATOR_SIZE)

        total_time_per_kb = 0
        successful_sizes = 0

        for stat in self.size_stats:
            size = stat["cache_size_kb"]
            status = stat["status"]
            avg_time = stat["avg_time_ns"]

            # Format the time column
            time_str = f"{avg_time:>15}" if avg_time is not None else " " * 15
            status_str = f"{status:>15}"

            print(f"| {size:>15} | {status_str} | {time_str} |")

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

    def print_object_stats(self):
        """Print object count statistics in table format"""
        if not self.object_stats:
            print("\nNo object count statistics collected")
            return

        print("\n=== Object Count Statistics ===")
        print(self.STATS_HEADER_OBJS)
        print(self.STATS_SEPARATOR_OBJS)

        total_time_per_kb = 0
        successful_objects = 0

        for stat in self.object_stats:
            num_objs = stat["num_objs"]
            status = stat["status"]
            avg_time = stat["avg_time_ns"]
            failed_at_obj = stat["failed_at_obj"]

            # Calculate total memory: successful allocations or partial allocation on failure
            if status == "SUCCESS":
                total_memory = stat["total_memory_kb"]
            elif status == "FAIL" and failed_at_obj is not None:
                total_memory = self.max_successful_size * failed_at_obj
            else:
                total_memory = 0

            # Format the columns
            time_str = f"{avg_time:>15}" if avg_time is not None else " " * 15
            status_str = f"{status:>15}"
            memory_str = f"{total_memory:>15}" if total_memory else " " * 15

            print(f"| {num_objs:>15} | {status_str} | {time_str} | {memory_str} |")

            # Calculate average time per KB for successful allocations
            if status == "SUCCESS" and avg_time is not None and total_memory > 0:
                time_per_kb = avg_time / total_memory
                total_time_per_kb += time_per_kb
                successful_objects += 1

        # Print average time per KB
        if successful_objects > 0:
            print(
                f"\nAverage allocation time per KB: {int(total_time_per_kb / successful_objects)} ns"
            )

    def run_all_tests(self):
        """Run all tests for ex_kmem_cache module"""
        print(f"=== Testing {self.module_name} module ===\n")

        try:
            # Run various test suites
            self.test_module_lifecycle()
            self.test_parameter_access()
            self.test_allocation_success()
            self.test_cache_size_sweep()
            self.test_object_count_sweep()

            # Print final summary
            return self.print_summary()

        except Exception as e:
            print(f"\n[!] Error during testing: {e}")
            self.failed_count += 1
            return self.print_summary()
