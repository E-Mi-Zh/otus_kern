#!/usr/bin/env python3
import os
import time
import subprocess
import re
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Kernel module tester')
    parser.add_argument('module_name', 
                      help='Name of the kernel module to test')
    # parser.add_argument('--module-path',
                    #   default=None,
                    #   help='Path to module file (default: ./<module_name>.ko)')
    return parser.parse_args()

args = parse_args()
module_name = args.module_name
# module_path = args.module_path if args.module_path else f"{module_name}.ko"

class KernelModuleTester:
    def __init__(self, module_name="ex_list"):
        self.module_name = module_name
        self.module_path = f"src/{module_name}.ko"
        self.sysfs_path = f"/sys/module/{module_name}/parameters"
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0

    def run_command(self, cmd, check=True):
        """Execute shell command and return result"""
        result = subprocess.run(cmd, shell=True, check=check,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
        return result.stdout.strip()

    def load_module(self):
        """Load kernel module"""
        print(f"[+] Loading module {self.module_name}...")
        self.run_command(f"sudo insmod {self.module_path}")
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
        """Check if dmesg contains pattern and print test result"""
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
            print(dmesg[-500:])  # Show last 500 chars of dmesg
            return False

    def test_module_lifecycle(self):
        """Test module load/unload"""
        print("\n=== Module Lifecycle Tests ===")
        self.clear_dmesg()

        # Test module loading
        self.load_module()
        self.assert_dmesg_contains(
            rf"{module_name} module loaded",
            "Module loading"
        )

        # Test module unloading
        self.unload_module()
        self.assert_dmesg_contains(
            rf"{module_name} module unloaded",
            "Module unloading"
        )

    def test_list_operations(self):
        """Test all list operations"""
        print("\n=== List Operation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # Test adding elements
            print("\n--- Add Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "add")
            self.assert_dmesg_contains(
                r"Added item: 10",
                "Add item 10"
            )

            self.set_parameter("value", 20)
            self.set_parameter("cmd", "add")
            self.assert_dmesg_contains(
                r"Added item: 20",
                "Add item 20"
            )

            # Test print operation
            print("\n--- Print Operation ---")
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"List contents:.*10 20",
                "Verify list contents [10, 20]"
            )

            # Test find operation
            print("\n--- Find Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "find")
            self.assert_dmesg_contains(
                r"Item 10 found in list",
                "Find existing item 10"
            )

            self.set_parameter("value", 99)
            self.set_parameter("cmd", "find")
            self.assert_dmesg_contains(
                r"Item 99 not found in list",
                "Find non-existent item 99"
            )

            # Test swap operation
            print("\n--- Swap Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "swap")
            self.assert_dmesg_contains(
                r"Swapped items: 20 and 10",
                "Swap items 10 and 20"
            )

            # Verify swap result
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"List contents:.*20 10",
                "Verify list after swap [20, 10]"
            )

            # Test reverse operation
            print("\n--- Reverse Operation ---")
            self.set_parameter("cmd", "reverse")
            self.assert_dmesg_contains(
                r"List reversed",
                "Reverse list"
            )

            # Verify reverse result
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"List contents:.*10 20",
                "Verify list after reverse [10, 20]"
            )

            # Test delete operation
            print("\n--- Delete Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "del")
            self.assert_dmesg_contains(
                r"Deleted item: 10",
                "Delete item 10"
            )

            # Verify delete result
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"List contents:.*20",
                "Verify list after deletion [20]"
            )

        finally:
            self.unload_module()

    def print_summary(self):
        """Print test summary"""
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
        """Run all tests"""
        try:
            self.test_module_lifecycle()
            self.test_list_operations()
            return self.print_summary()

        except Exception as e:
            print(f"\n[!] Test error: {e}")
            with open("dmesg_failure.log", "w") as f:
                f.write(self.get_dmesg_output())
            print("Debug info saved to dmesg_failure.log")
            return 1

if __name__ == "__main__":
    tester = KernelModuleTester(module_name)

    if not os.path.exists(tester.module_path):
        print(f"[!] Error: Module file {tester.module_path} not found")
        print("Please build the module first using make")
        exit(1)

    exit_code = tester.run_all_tests()
    exit(exit_code)