#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class ExVmallocTester(BaseModuleTester):
    STATS_HEADER = "| Requested (kb) | Allocated (kb) | Time (ns)     |"
    STATS_SEPARATOR = "|----------------|----------------|---------------|"

    def __init__(self, module_name):
        super().__init__(module_name)
        self.default_alloc_size = 4  # Default allocation size in KB
        self.allocation_stats = []

    def test_parameter_access(self):
        """Test reading and writing module parameters"""
        print("\n=== Module Parameter Tests ===")
        self.clear_dmesg()
        self.load_module()

        # Test reading default parameter value
        param_value = self.get_parameter("alloc_size_kb")
        if param_value and param_value == str(self.default_alloc_size):
            self.test_count += 1
            self.passed_count += 1
            print(
                f"Test #{self.test_count}: Default parameter value is {param_value} - PASS"
            )
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Default parameter value check - FAIL")

        # Test setting parameter to one value
        test_value = 8
        if self.set_parameter("alloc_size_kb", str(test_value)):
            self.test_count += 1
            self.passed_count += 1
            print(f"Test #{self.test_count}: Set parameter to {test_value} KB - PASS")
        else:
            self.test_count += 1
            self.failed_count += 1
            print(f"Test #{self.test_count}: Set parameter to {test_value} KB - FAIL")

        self.unload_module()

    def test_allocation_success(self):
        """Test successful memory allocation with default size"""
        print("\n=== Allocation Success Test ===")
        self.clear_dmesg()
        self.load_module()

        # Check for successful allocation message
        success = self.assert_dmesg_contains(
            r"vmalloc: SUCCESS", "Memory allocation successful"
        )

        # Check for allocation details
        if success:
            self.assert_dmesg_contains(
                r"vmalloc: \d+ byte, \d+ ns, type: VIRTUAL_NON_CONTIGUOUS",
                "Allocation details with timing",
            )

        self.unload_module()

    def parse_allocation_stats(self, dmesg_output, requested_kb):
        """Parse allocation statistics from dmesg output"""
        # Pattern for successful allocation
        success_pattern = rf"vmalloc: ({requested_kb}|\d+) byte.*vmalloc: SUCCESS.*vmalloc: (\d+) byte, (\d+) ns"
        success_match = re.search(success_pattern, dmesg_output, re.DOTALL)
        
        if success_match:
            allocated_bytes = int(success_match.group(2))
            time_ns = int(success_match.group(3))
            allocated_kb = allocated_bytes // 1024
            return allocated_kb, time_ns
        
        # Pattern for failed allocation
        fail_pattern = r"vmalloc: FAIL"
        if re.search(fail_pattern, dmesg_output):
            return "FAIL", None
        
        return None, None

    def test_allocation_with_different_sizes(self):
        """Test allocation with different size parameters"""
        print("\n=== Different Allocation Sizes Test ===")

        # Generate size series: doubling until 1024 MB (in KB)
        test_sizes = []
        size = 1  # Start from 1 KB
        while size <= 32 * 1024 * 1024:  # 32 * 1024 MB in KB
            test_sizes.append(size)
            size *= 2
        
        self.allocation_stats = []  # Reset stats for this test run

        for size in test_sizes:
            print(f"\n--- Testing allocation size: {size} KB ---")
            self.clear_dmesg()
            # Load module with parameter
            self.load_module(f"alloc_size_kb={size}")
            
            # Parse allocation statistics from dmesg
            dmesg_output = self.get_dmesg_output()
            allocated, time_ns = self.parse_allocation_stats(dmesg_output, size)
            
            if allocated is not None:
                self.allocation_stats.append({
                    'requested_kb': size,
                    'allocated_kb': allocated,
                    'time_ns': time_ns
                })
                status = "SUCCESS" if allocated != "FAIL" else "FAIL"
                print(f"Allocation result: {status}")
                if time_ns:
                    print(f"Allocation time: {time_ns} ns")
            else:
                print("Warning: Could not parse allocation statistics from dmesg")
                self.allocation_stats.append({
                    'requested_kb': size,
                    'allocated_kb': "UNKNOWN",
                    'time_ns': None
                })

            # Check for allocation with correct size
            self.assert_dmesg_contains(
                rf"vmalloc: {size * 1024} byte", f"Allocation with size {size} KB"
            )

            self.unload_module()
        
        # Print statistics table after all size tests
        self.print_allocation_stats()

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
            rf"\[EXIT\] {self.module_name} module unloaded",
            "Module unload message"
        )

    def print_allocation_stats(self):
        """Print allocation statistics in table format"""
        if not self.allocation_stats:
            print("\nNo allocation statistics collected")
            return
        
        print("\n=== Allocation Statistics ===")
        print(self.STATS_HEADER)
        print(self.STATS_SEPARATOR)
        
        total_time = 0
        successful_allocations = 0
        
        for stat in self.allocation_stats:
            requested = stat['requested_kb']
            allocated = stat['allocated_kb']
            time_ns = stat['time_ns']
            
            # Format the time column
            time_str = f"{time_ns:>13}" if time_ns is not None else " " * 13
            
            print(f"| {requested:>14} | {allocated!s:>14} | {time_str} |")
            
            # Calculate average time for successful allocations
            if time_ns is not None:
                total_time += time_ns
                successful_allocations += 1
        
        # Print average time
        if successful_allocations > 0:
            print(f"\nAverage allocation time: {total_time // successful_allocations} ns")

    def run_all_tests(self):
        """Run all tests for ex_vmalloc module"""
        print(f"=== Testing {self.module_name} module ===\n")

        try:
            # Run various test suites
            self.test_module_lifecycle()
            self.test_parameter_access()
            self.test_allocation_success()
            self.test_allocation_with_different_sizes()

            # Print final summary
            return self.print_summary()

        except Exception as e:
            print(f"\n[!] Error during testing: {e}")
            self.failed_count += 1
            return self.print_summary()