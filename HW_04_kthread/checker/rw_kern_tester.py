#!/usr/bin/env python3
import time
import re
from .base_tester import BaseModuleTester


class RWModuleTester(BaseModuleTester):
    def test_rw_operations(self):
        """Test reader-writer module functionality"""
        print("\n=== Reader-Writer Operation Tests ===")
        self.clear_dmesg()
        self.load_module()

        try:
            # Даем время потокам поработать
            time.sleep(1.0)

            # Check initialization
            print("\n--- Thread Creation Test ---")
            self.assert_dmesg_contains_ex(
                r"Reader-Writer kernel module: Initializing",
                "Module initialization message",
            )

            # Check that operations are happening
            print("\n--- Reader Operations Test ---")
            self.assert_dmesg_contains_ex(
                r"Reader \d+: read value = \d+, iteration = \d+",
                "Reader operations are happening",
            )

            print("\n--- Writer Operations Test ---")
            self.assert_dmesg_contains_ex(
                r"Writer \d+: wrote value = \d+, iteration = \d+",
                "Writer operations are happening",
            )

        finally:
            # Выгружаем модуль - статистика будет выведена в rw_exit()
            self.unload_module()

            # Даем время для вывода статистики
            time.sleep(0.5)

            self.check_final_stats()

    def check_final_stats(self):
        """Check final statistics after module unload"""
        print("\n=== Final Statistics Test ===")

        dmesg = self.get_dmesg_output()

        # Check that statistics section exists
        self.assert_dmesg_contains(
            r"=== KERNEL STATISTICS ===", "Statistics section header"
        )

        # Check readers completion (informational only)
        reader_pattern = r"Reader (\d+) completed (\d+)/20 iterations"
        reader_matches = re.findall(reader_pattern, dmesg)
        for reader_id, completed in reader_matches:
            print(f"Reader {reader_id}: {completed}/20 iterations")

        # Check writers completion (informational only)
        writer_pattern = r"Writer (\d+) completed (\d+)/20 iterations"
        writer_matches = re.findall(writer_pattern, dmesg)
        for writer_id, completed in writer_matches:
            print(f"Writer {writer_id}: {completed}/20 iterations")

        # Check final counter value
        self.assert_dmesg_contains(
            r"Final value of shared_data: \d+", "Final counter value reported"
        )

    def run_all_tests(self):
        """Execute all reader-writer module tests"""
        try:
            self.test_module_lifecycle()
            self.test_rw_operations()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            import traceback

            traceback.print_exc()

            # Save debug info
            dmesg_output = self.get_dmesg_output()
            with open("dmesg_failure.log", "w") as f:
                f.write(dmesg_output)
            print("Debug info saved to dmesg_failure.log")

            # Try to unload module if something went wrong
            try:
                self.unload_module()
            except:
                pass

            return 1
