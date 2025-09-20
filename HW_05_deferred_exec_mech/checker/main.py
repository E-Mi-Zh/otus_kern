#!/usr/bin/env python3
import argparse
import os
import sys

# Add path to test scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from checker.base_tester import BaseModuleTester
from checker.softirq_tester import SoftirqTester
from checker.tasklet_tester import TaskletTester
from checker.workqueue_tester import WorkqueueTester


def main():
    """Main entry point for module testing"""
    parser = argparse.ArgumentParser(
        description="Kernel module and userspace program tester"
    )
    parser.add_argument(
        "test_type",
        choices=["softirq", "tasklet", "workqueue"],
        help="Test type: softirq for ex_softirq kernel module, tasklet for "
        "ex_tasklet kernel module, workqueue for ex_workqueue kernel module",
    )
    parser.add_argument("target_name", help="Name of the target to test")
    args = parser.parse_args()

    if args.test_type == "softirq":
        # Kernel module testing
        tester = SoftirqTester(args.target_name)

        # Verify module exists
        module_path = (
            f"/lib/modules/{os.uname().release}/extra/src/{args.target_name}.ko"
        )
        if not os.path.exists(module_path):
            module_path = f"./{args.target_name}.ko"
            if not os.path.exists(module_path):
                print(f"[!] Error: Module file {args.target_name}.ko not found")
                print("Please build the module first using 'make'")
                exit(1)

    elif args.test_type == "tasklet":
        # Tasklet module testing
        tester = TaskletTester(args.target_name)
        module_path = (
            f"/lib/modules/{os.uname().release}/extra/src/{args.target_name}.ko"
        )
        if not os.path.exists(module_path):
            module_path = f"./{args.target_name}.ko"
            if not os.path.exists(module_path):
                print(f"[!] Error: Module file {args.target_name}.ko not found")
                print("Please build the module first using 'make'")
                exit(1)

    elif args.test_type == "workqueue":
        # Workqueue module testing
        tester = WorkqueueTester(args.target_name)
        module_path = (
            f"/lib/modules/{os.uname().release}/extra/src/{args.target_name}.ko"
        )
        if not os.path.exists(module_path):
            module_path = f"./{args.target_name}.ko"
            if not os.path.exists(module_path):
                print(f"[!] Error: Module file {args.target_name}.ko not found")
                print("Please build the module first using 'make'")
                exit(1)

    # Run tests
    exit_code = tester.run_all_tests()
    exit(exit_code)


if __name__ == "__main__":
    main()
