#!/usr/bin/env python3
from .base_tester import BaseModuleTester

class QueueModuleTester(BaseModuleTester):
    def test_queue_operations(self):
        """Queue-specific test operations"""
        print("\n=== Queue Operation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # Test enqueue operation
            print("\n--- Enqueue Operation ---")
            self.set_parameter("value", 10)
            self.set_parameter("cmd", "enqueue")
            self.assert_dmesg_contains(
                r"Enqueued: 10",
                "Enqueue item 10"
            )

            self.set_parameter("value", 20)
            self.set_parameter("cmd", "enqueue")
            self.assert_dmesg_contains(
                r"Enqueued: 20",
                "Enqueue item 20"
            )

            # Test peek operation
            print("\n--- Peek Operation ---")
            self.set_parameter("cmd", "peek")
            self.assert_dmesg_contains(
                r"Front item: 10",
                "Peek should show first item 10"
            )

            # Test print operation
            print("\n--- Print Operation ---")
            self.set_parameter("cmd", "print")
            self.assert_dmesg_contains(
                r"Queue contents.*10 20",
                "Queue should contain [10, 20]"
            )

            # Test total operation
            print("\n--- Total Operation ---")
            self.set_parameter("cmd", "total")
            self.assert_dmesg_contains(
                r"Sum of values.*30",
                "Sum of values should be equal 30"
            )

            # Test dequeue operation
            print("\n--- Dequeue Operation ---")
            self.set_parameter("cmd", "dequeue")
            self.assert_dmesg_contains(
                r"Dequeued: 10",
                "Dequeue should return first item 10"
            )

            # Test total operation
            print("\n--- Total Operation ---")
            self.set_parameter("cmd", "total")
            self.assert_dmesg_contains(
                r"Sum of values.*20",
                "Sum of values should be equal 20"
            )


            # Test clear operation
            print("\n--- Clear Operation ---")
            self.set_parameter("cmd", "clear")
            self.assert_dmesg_contains(
                r"Queue cleared",
                "Clear queue"
            )

        finally:
            self.unload_module()

    def run_all_tests(self):
        """Execute all queue module tests"""
        try:
            self.test_module_lifecycle()
            self.test_queue_operations()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            with open("dmesg_failure.log", "w") as f:
                f.write(self.get_dmesg_output())
            print("Debug info saved to dmesg_failure.log")
            return 1
