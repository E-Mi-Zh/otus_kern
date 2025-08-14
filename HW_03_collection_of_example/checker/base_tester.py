#!/usr/bin/env python3
import os
import time
import subprocess
import re

class BaseModuleTester:
    def __init__(self, module_name):
        self.module_name = module_name
        #self.module_path = f"{module_name}.ko"
        self.module_path = module_name
        self.sysfs_path = f"/sys/module/{module_name}/parameters"
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0

    def run_command(self, cmd, check=True):
        """Execute shell commands and return result"""
        result = subprocess.run(cmd, shell=True, check=check,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
        return result.stdout.strip()

    def load_module(self):
        """Load kernel module"""
        print(f"[+] Loading module {self.module_name}...")
        self.run_command(f"sudo modprobe {self.module_name}")
        time.sleep(0.5)

    def unload_module(self):
        """Unload kernel module"""
        print(f"[+] Unloading module {self.module_name}...")
        self.run_command(f"sudo rmmod {self.module_name}")
        time.sleep(0.5)

    def set_parameter(self, param, value):
        """Set module parameter via sysfs"""
        param_path = f"{self.sysfs_path}/{param}"
        self.run_command(f"echo {value} | sudo tee {param_path}")
        time.sleep(0.2)

    def get_dmesg_output(self):
        """Get dmesg output"""
        return self.run_command("dmesg")

    def clear_dmesg(self):
        """Clear dmesg buffer"""
        self.run_command("sudo dmesg -C")

    def assert_dmesg_contains(self, pattern, expected_msg):
        """Check if dmesg contains specified pattern"""
        self.test_count += 1
        dmesg = self.get_dmesg_output()
        match = re.search(pattern, dmesg)

        print(f"\nTest #{self.test_count}")
        print(f"Command:    {expected_msg}")
        print(f"Expected:   Pattern '{pattern}'")
        print(f"Found:      {'Yes' if match else 'No'}")

        if match:
            self.passed_count += 1
            print("Result:     PASS")
            return True
        else:
            self.failed_count += 1
            print("Result:     FAIL")
            print("Debug info:")
            print(dmesg[-500:])  # Show last 500 characters of log
            return False

    def test_module_lifecycle(self):
        """Test module loading/unloading"""
        print("\n=== Module Lifecycle Tests ===")
        self.clear_dmesg()

        self.load_module()
        self.assert_dmesg_contains(
            rf"{self.module_name} module loaded",
            "Module loading"
        )

        self.unload_module()
        self.assert_dmesg_contains(
            rf"{self.module_name} module unloaded",
            "Module unloading"
        )

    def print_summary(self):
        """Print test summary report"""
        print("\n=== Test Summary ===")
        print(f"Total tests:  {self.test_count}")
        print(f"Passed:       {self.passed_count}")
        print(f"Failed:       {self.failed_count}")
        print(f"Success rate: {self.passed_count/self.test_count*100:.1f}%")

        if self.failed_count == 0:
            print("\nFINAL RESULT: ALL TESTS PASSED")
            return 0
        else:
            print("\nFINAL RESULT: SOME TESTS FAILED")
            return 1

    def run_all_tests(self):
        """Main test runner (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement run_all_tests()")
