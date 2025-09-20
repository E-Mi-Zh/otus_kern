#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class TaskletTester(BaseModuleTester):
    def __init__(self, module_name):
        super().__init__(module_name)
        self.max_tasklet_executions = 15
        self.timer_interval_ms = 1000

    def run_all_tests(self):
        """Run all tests for the tasklet module"""
        try:
            print(f"=== Testing {self.module_name} Module ===")

            # Test 1: Module lifecycle
            self.test_module_lifecycle()

            # Test 2: Timer and tasklet functionality
            self.test_timer_tasklet_functionality()

            # Test 3: Tasklet execution limit
            self.test_tasklet_limit()

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

    def test_timer_tasklet_functionality(self):
        """Test timer and tasklet functionality"""
        print("\n=== Timer and Tasklet Functionality Tests ===")
        self.clear_dmesg()

        # Load module
        self.load_module()
        time.sleep(0.5)

        # Check if module initialized correctly
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*module loaded", "Module initialization message"
        )

        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Timer start.*interval.*{self.timer_interval_ms}.*ms",
            "Timer startup message",
        )

        # Wait for timer to trigger a few times
        print(
            f"[+] Waiting for timer to trigger (approx {self.timer_interval_ms * 2}ms)..."
        )
        time.sleep(self.timer_interval_ms * 2 / 1000 + 0.5)

        # Check for timer and tasklet activity
        dmesg = self.get_dmesg_output()

        # Check for timer triggers
        timer_pattern = (
            rf"{self.module_name}: \[TIMER\] Trigger \d+\. Scheduling tasklet"
        )
        timer_matches = len(re.findall(timer_pattern, dmesg, re.IGNORECASE))
        print(f"[+] Found {timer_matches} timer triggers")

        # Check for tasklet executions
        tasklet_pattern = (
            rf"{self.module_name}: \[TASKLET\] Execution \d+\. Timer triggered \d+"
        )
        tasklet_matches = len(re.findall(tasklet_pattern, dmesg, re.IGNORECASE))
        print(f"[+] Found {tasklet_matches} tasklet executions")

        # Verify we have both timer and tasklet activity
        self.test_count += 1
        print(f"\nTest #{self.test_count}")
        print("Command:    Timer and tasklet functionality")
        print(f"Expected:   Timer triggers > 0 and tasklet executions > 0")
        print(f"Found:      Timer={timer_matches}, Tasklet={tasklet_matches}")

        if timer_matches > 0 and tasklet_matches > 0:
            self.passed_count += 1
            print("Result:     PASS")
        else:
            self.failed_count += 1
            print("Result:     FAIL")

        # Unload module and check statistics
        self.unload_module()

        # Check for statistics in exit message
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Statistics.*Timer.*\d+.*Tasklet.*\d+",
            "Module statistics on exit",
        )

        # Check for tasklet kill message
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Timer stopped", "Timer stop message"
        )

    def test_tasklet_limit(self):
        """Test that tasklet execution stops at the limit"""
        print("\n=== Tasklet Execution Limit Test ===")
        self.clear_dmesg()

        # Load module
        self.load_module()
        time.sleep(0.5)

        # Wait for enough time to reach the execution limit
        wait_time = (self.max_tasklet_executions + 2) * self.timer_interval_ms / 1000
        print(f"[+] Waiting for tasklet execution limit ({wait_time:.1f}s)...")
        time.sleep(wait_time)

        # Check for the limit reached message
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Execution limit.*{self.max_tasklet_executions}.*reached.*stopping timer",
            "Tasklet execution limit reached",
        )

        # Unload module
        self.unload_module()
