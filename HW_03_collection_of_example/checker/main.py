#!/usr/bin/env python3
import argparse
import os
import sys

# Add path to test scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checker.list_tester import ListModuleTester
from checker.queue_tester import QueueModuleTester
from checker.rb_tree_tester import RB_TreeModuleTester
from checker.bitmap_tester import BitmapModuleTester
from checker.bin_search_tester import BSearchModuleTester
from checker.bin_tree_tester import Bin_TreeModuleTester


def main():
    """Main entry point for module testing"""
    parser = argparse.ArgumentParser(description="Kernel module tester")
    parser.add_argument(
        "module_type",
        choices=["list", "queue", "rb_tree", "bitmap", "bin_search", "bin_tree"],
        help="Module type to test (list, queue, rb_tree, bitmap, bin_search or bin_tree)",
    )
    parser.add_argument("module_name", help="Name of the kernel module to test")
    args = parser.parse_args()

    # Initialize appropriate tester
    testers = {
        "list": ListModuleTester,
        "queue": QueueModuleTester,
        "rb_tree": RB_TreeModuleTester,
        "bitmap": BitmapModuleTester,
        "bin_search": BSearchModuleTester,
        "bin_tree": Bin_TreeModuleTester,
    }
    tester = testers[args.module_type](args.module_name)

    # Verify module exists
    if not os.path.exists(
        f"/lib/modules/{os.uname().release}/extra/src/{args.module_name}.ko"
    ):
        print(f"[!] Error: Module file {args.module_name}.ko not found")
        print(
            "Please build and install the module first using 'make' & 'sudo make install'"
        )
        exit(1)

    # Run tests
    exit_code = tester.run_all_tests()
    exit(exit_code)


if __name__ == "__main__":
    main()
