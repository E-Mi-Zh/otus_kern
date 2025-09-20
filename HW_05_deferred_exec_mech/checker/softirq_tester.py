#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class SoftirqTester(BaseModuleTester):
    def __init__(self, module_name):
        super().__init__(module_name)
        self.max_softirq_executions = 15
        self.timer_interval_ms = 1000

    def run_all_tests(self):
        """Run all tests for the ex_softirq module"""
        try:
            print(f"=== Testing {self.module_name} Module ===")

            # Test 1: Module lifecycle
            self.test_module_lifecycle()

            # Test 2: Timer functionality
            self.test_timer_functionality()

            # Test 3: Softirq execution limit
            self.test_softirq_limit()

            # Print summary
            return self.print_summary()

        except Exception as e:
            print(f"[!] Error during testing: {e}")
            return 1
        finally:
            # Ensure module is unloaded
            try:
                self.unload_module()
            except:
                pass

    def test_timer_functionality(self):
        """Test timer and softirq functionality"""
        print("\n=== Timer and Softirq Functionality Tests ===")
        self.clear_dmesg()

        # Load module
        self.load_module()
        time.sleep(0.5)

        # Check if module initialized correctly
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*ex_softirq module loaded",
            "Module initialization message",
        )

        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Register softirq handler",
            "Softirq handler registration",
        )

        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Timer start, interval {self.timer_interval_ms} ms",
            "Timer startup message",
        )

        # Wait for timer to trigger a few times
        print(
            f"[+] Waiting for timer to trigger (approx {self.timer_interval_ms * 2}ms)..."
        )
        time.sleep(self.timer_interval_ms * 2 / 1000 + 0.5)

        # Check for timer and softirq activity
        dmesg = self.get_dmesg_output()

        # Check for timer triggers
        timer_pattern = rf"{self.module_name}: \[TIMER\] Trigger \d+\. Raising softirq"
        timer_matches = len(re.findall(timer_pattern, dmesg))
        print(f"[+] Found {timer_matches} timer triggers")

        # Check for softirq executions
        softirq_pattern = (
            rf"{self.module_name}: \[SOFTIRQ\] Execution \d+\. Timer triggered \d+"
        )
        softirq_matches = len(re.findall(softirq_pattern, dmesg))
        print(f"[+] Found {softirq_matches} softirq executions")

        # Verify we have both timer and softirq activity
        self.test_count += 1
        print(f"\nTest #{self.test_count}")
        print("Command:    Timer and softirq functionality")
        print(f"Expected:   Timer triggers > 0 and softirq executions > 0")
        print(f"Found:      Timer={timer_matches}, Softirq={softirq_matches}")

        if timer_matches > 0 and softirq_matches > 0:
            self.passed_count += 1
            print("Result:     PASS")
        else:
            self.failed_count += 1
            print("Result:     FAIL")

        # Unload module and check statistics
        self.unload_module()

        # Check for statistics in exit message
        self.assert_dmesg_contains(
            rf"{self.module_name}: \[EXIT\] Statistics: Timer=\d+, Softirq=\d+",
            "Module statistics on exit",
        )

    def test_softirq_limit(self):
        """Test that softirq execution stops at the limit"""
        print("\n=== Softirq Execution Limit Test ===")
        self.clear_dmesg()

        # Load module
        self.load_module()
        time.sleep(0.5)

        # Wait for enough time to reach the execution limit
        # Each execution takes ~1 second, so wait for enough time
        wait_time = (self.max_softirq_executions + 2) * self.timer_interval_ms / 1000
        print(f"[+] Waiting for softirq execution limit ({wait_time:.1f}s)...")
        time.sleep(wait_time)

        # Check for the limit reached message
        self.assert_dmesg_contains(
            rf"{self.module_name}: \[TIMER\] Execution limit {self.max_softirq_executions} reached, stopping timer",
            "Softirq execution limit reached",
        )

        # Unload module
        self.unload_module()
