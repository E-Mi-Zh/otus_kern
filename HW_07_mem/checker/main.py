#!/usr/bin/env python3
import argparse
import os
import sys

# Add path to test scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checker.base_tester import BaseModuleTester
from checker.kmalloc_tester import ExKmallocTester
from checker.vmalloc_tester import ExVmallocTester
from checker.kmem_cache_tester import ExKmemCacheTester


def main():
    """Main entry point for module testing"""
    parser = argparse.ArgumentParser(
        description="Kernel memory allocation modules tester"
    )
    parser.add_argument(
        "test_type",
        choices=["kmalloc", "vmalloc", "kmem_cache"],
        help="Test type: kmalloc for kmalloc testing module, vmalloc for vmalloc testing module, kmem_cache for kmem_cache testing module",
    )
    parser.add_argument("target_name", help="Name of the target to test")
    args = parser.parse_args()

    if args.test_type == "kmalloc":
        # Kernel module testing
        tester = ExKmallocTester("ex_kmalloc")
        module_name = "ex_kmalloc"
    elif args.test_type == "vmalloc":
        # Kernel module testing
        tester = ExVmallocTester("ex_vmalloc")
        module_name = "ex_vmalloc"
    elif args.test_type == "kmem_cache":
        # Kernel module testing
        tester = ExKmemCacheTester("ex_kmem_cache")
        module_name = "ex_kmem_cache"

    # Verify module exists
    module_path = f"/lib/modules/{os.uname().release}/extra/src/{args.target_name}.ko"
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
