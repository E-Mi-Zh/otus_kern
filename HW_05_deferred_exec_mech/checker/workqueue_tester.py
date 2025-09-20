#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class WorkqueueTester(BaseModuleTester):
    def __init__(self, module_name):
        super().__init__(module_name)
        self.max_work_executions = 15
        self.timer_interval_ms = 1000

    def run_all_tests(self):
        """Run all tests for the workqueue module"""
        try:
            print(f"=== Testing {self.module_name} Module ===")

            # Test 1: Module lifecycle
            self.test_module_lifecycle()

            # Test 2: Timer and workqueue functionality
            self.test_timer_workqueue_functionality()

            # Test 3: Work execution limit
            self.test_work_limit()

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

    def test_timer_workqueue_functionality(self):
        """Test timer and workqueue functionality"""
        print("\n=== Timer and Workqueue Functionality Tests ===")
        self.clear_dmesg()

        # Load module
        self.load_module()
        time.sleep(0.5)

        # Check if module initialized correctly
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*module loaded", "Module initialization message"
        )

        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Workqueue initialized", "Workqueue initialization"
        )

        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Timer started.*interval.*{self.timer_interval_ms}.*ms",
            "Timer startup message",
        )

        # Wait for timer to trigger a few times
        print(
            f"[+] Waiting for timer to trigger (approx {self.timer_interval_ms * 2}ms)..."
        )
        time.sleep(self.timer_interval_ms * 2 / 1000 + 0.5)

        # Check for timer and work activity
        dmesg = self.get_dmesg_output()

        # Check for timer triggers
        timer_pattern = rf"{self.module_name}: \[TIMER\] Trigger \d+\. Queueing work"
        timer_matches = len(re.findall(timer_pattern, dmesg, re.IGNORECASE))
        print(f"[+] Found {timer_matches} timer triggers")

        # Check for work executions
        work_pattern = (
            rf"{self.module_name}: \[WORKQUEUE\] Execution \d+\. Timer triggered \d+"
        )
        work_matches = len(re.findall(work_pattern, dmesg, re.IGNORECASE))
        print(f"[+] Found {work_matches} work executions")

        # Verify we have both timer and work activity
        self.test_count += 1
        print(f"\nTest #{self.test_count}")
        print("Command:    Timer and workqueue functionality")
        print(f"Expected:   Timer triggers > 0 and work executions > 0")
        print(f"Found:      Timer={timer_matches}, Work={work_matches}")

        if timer_matches > 0 and work_matches > 0:
            self.passed_count += 1
            print("Result:     PASS")
        else:
            self.failed_count += 1
            print("Result:     FAIL")

        # Unload module and check cleanup messages
        self.unload_module()

        # Check for cleanup messages
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Timer stopped", "Timer stop message"
        )

        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Work cancelled.*workqueue deleted",
            "Workqueue cleanup message",
        )

        # Check for statistics in exit message
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Statistics.*Timer.*\d+.*Work.*\d+",
            "Module statistics on exit",
        )

    def test_work_limit(self):
        """Test that work execution stops at the limit"""
        print("\n=== Work Execution Limit Test ===")
        self.clear_dmesg()

        # Load module
        self.load_module()
        time.sleep(0.5)

        # Wait for enough time to reach the execution limit
        wait_time = (self.max_work_executions + 2) * self.timer_interval_ms / 1000
        print(f"[+] Waiting for work execution limit ({wait_time:.1f}s)...")
        time.sleep(wait_time)

        # Check for the limit reached message
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Execution limit.*{self.max_work_executions}.*reached.*stopping timer",
            "Work execution limit reached",
        )

        # Unload module
        self.unload_module()
