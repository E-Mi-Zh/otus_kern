#!/usr/bin/env python3
import argparse
import os
import sys

# Add path to test scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checker.list_tester import ListModuleTester
from checker.queue_tester import QueueModuleTester

def main():
    """Main entry point for module testing"""
    parser = argparse.ArgumentParser(description='Kernel module tester')
    parser.add_argument('module_type', choices=['list', 'queue'],
                      help='Module type to test (list or queue)')
    parser.add_argument('module_name',
                      help='Name of the kernel module to test')
    args = parser.parse_args()

    # Initialize appropriate tester
    tester = None
    if args.module_type == 'list':
        tester = ListModuleTester(args.module_name)
    else:
        tester = QueueModuleTester(args.module_name)

    # Verify module exists
    if not os.path.exists(f"/lib/modules/{os.uname().release}/extra/src/{args.module_name}.ko"):
        print(f"[!] Error: Module file {args.module_name}.ko not found")
        print("Please build and install the module first using 'make' & 'sudo make install'")
        exit(1)

    # Run tests
    exit_code = tester.run_all_tests()
    exit(exit_code)

if __name__ == "__main__":
    main()
