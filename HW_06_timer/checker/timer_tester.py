#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class TimerTester(BaseModuleTester):
    def __init__(self, module_name):
        super().__init__(module_name)
        self.timer_interval_ms = 30000  # 30 seconds
        self.total_timer_ms = 300000  # 5 minutes = 300 seconds
        self.max_triggers = 10  # 300000 / 30000 = 10 triggers

    def run_all_tests(self):
        """Run all tests for the timer module"""
        try:
            print(f"=== Testing {self.module_name} Module ===")

            # Test 1: Module lifecycle
            self.test_module_lifecycle()

            # Test 2: Timer functionality with limited runtime
            self.test_timer_functionality_short()

            # Test 3: Full duration test
            self.test_timer_full_duration()

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

    def test_timer_functionality_short(self):
        """Test timer functionality with reduced wait time for testing"""
        print("\n=== Timer Functionality Tests (Short Version) ===")
        self.clear_dmesg()

        # Load module
        self.load_module()
        time.sleep(0.5)

        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Timer started.*Will trigger every.*seconds",
            "Timer startup message",
        )

        # Wait for timer to trigger (need to wait at least 30 seconds for first trigger)
        test_wait_seconds = 35  # Wait for 35 seconds to catch at least one trigger
        print(f"[+] Waiting for timer to trigger ({test_wait_seconds}s)...")
        time.sleep(test_wait_seconds)

        # Check for timer activity
        dmesg = self.get_dmesg_output()

        # Check for timer triggers
        timer_pattern = rf"{self.module_name}:.*min=\d+:.*Hello, timer!"
        timer_matches = len(re.findall(timer_pattern, dmesg, re.IGNORECASE))
        print(f"[+] Found {timer_matches} timer triggers in {test_wait_seconds}s")

        # Check for timer stop message (if it reached limit during our wait)
        stop_pattern = (
            rf"{self.module_name}: \[TIMER\] Timer stopped after \d+ triggers"
        )
        stop_matches = len(re.findall(stop_pattern, dmesg, re.IGNORECASE))

        # Verify we have timer activity
        self.test_count += 1
        print(f"\nTest #{self.test_count}")
        print("Command:    Timer functionality")
        print(f"Expected:   Timer triggers > 0")
        print(f"Found:      Timer triggers={timer_matches}")

        if timer_matches > 0:
            self.passed_count += 1
            print("Result:     PASS")

            # Check timing pattern (minute calculation)
            minute_pattern = rf"{self.module_name}:.*min=(\d+):.*Hello, timer!"
            minute_matches = re.findall(minute_pattern, dmesg, re.IGNORECASE)
            if minute_matches:
                print(f"[+] Minute pattern matches: {minute_matches}")
        else:
            self.failed_count += 1
            print("Result:     FAIL")

        # Unload module and check runtime statistics
        self.unload_module()

        # Check for runtime statistics
        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Total triggers:.*\d+",
            "Total triggers message",
        )

        self.assert_dmesg_contains(
            rf"{self.module_name}:.*Total runtime:.*\d+ minutes.*\d+ seconds",
            "Runtime statistics",
        )

    def test_timer_full_duration(self):
        print("\n=== Full Duration Timer Test (5 minutes) ===")
        # Uncomment below to run full test
        self.clear_dmesg()
        self.load_module()

        # Wait for full 5 minutes + buffer
        full_wait_minutes = 5.5
        print(f"[+] Waiting for full timer duration ({full_wait_minutes} minutes)...")
        time.sleep(full_wait_minutes * 60)

        # Check if timer stopped correctly after 10 triggers
        dmesg = self.get_dmesg_output()

        stop_pattern = (
            rf"{self.module_name}:.*Timer stopped after 10 triggers.*5 minutes"
        )
        stop_match = re.search(stop_pattern, dmesg, re.IGNORECASE)

        self.test_count += 1
        print(f"\nTest #{self.test_count}")
        print("Command:    Full duration timer test")
        print("Expected:   Timer stops after 10 triggers (5 minutes)")
        print(f"Found:      {'Yes' if stop_match else 'No'}")

        if stop_match:
            self.passed_count += 1
            print("Result:     PASS")
        else:
            self.failed_count += 1
            print("Result:     FAIL")
            print("Debug info:")
            print(dmesg[-1000:])

        self.unload_module()
