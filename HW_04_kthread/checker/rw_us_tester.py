#!/usr/bin/env python3
import os
import time
import subprocess
import re


class RWUsTester:
    def __init__(self, program_path):
        self.program_path = program_path
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.output = ""

    def run_command(self, cmd, check=True):
        """Execute shell commands and return result"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            # Command failed, but we want to capture output anyway
            return e.stdout.strip(), e.stderr.strip()
        except FileNotFoundError:
            return "", f"Command not found: {cmd}"

    def run_program(self):
        """Run the userspace program and capture output"""
        print(os.getcwd())
        print(f"[+] Running userspace program: {self.program_path}")
        stdout, stderr = self.run_command(self.program_path)

        # Check if program was not found
        if "Command not found" in stderr:
            # Try with ./ prefix
            alt_path = f"./{self.program_path}"
            print(f"[!] Program not found, trying: {alt_path}")
            stdout, stderr = self.run_command(alt_path)

        if stderr:
            print(f"[!] Program stderr: {stderr}")

        self.output = stdout
        return stdout

    def assert_output_contains(self, pattern, expected_msg):
        """Check if program output contains specified pattern"""
        self.test_count += 1
        match = re.search(pattern, self.output, re.DOTALL)

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
            print(f"Output: {self.output[-500:]}")
            return False

    def test_program_execution(self):
        """Test userspace program functionality"""
        print("\n=== Userspace Program Tests ===")

        # Run the program
        output = self.run_program()

        # Check initialization message
        print("\n--- Initialization Test ---")
        self.assert_output_contains(
            r"Reader-Writer userspace program: Initializing",
            "Program initialization message",
        )

        # Check reader operations
        print("\n--- Reader Operations Test ---")
        self.assert_output_contains(
            r"Reader \d+: read value = \d+, iteration = \d+",
            "Reader operations are happening",
        )

        # Check writer operations
        print("\n--- Writer Operations Test ---")
        self.assert_output_contains(
            r"Writer \d+: wrote value = \d+, iteration = \d+",
            "Writer operations are happening",
        )

        # Check statistics output
        print("\n--- Statistics Test ---")
        self.assert_output_contains(
            r"=== USERSPACE STATISTICS ===", "Statistics section header"
        )

        # Check final counter value
        print("\n--- Final Counter Value Test ---")
        self.assert_output_contains(
            r"Final value of shared_data: \d+", "Final counter value reported"
        )

        # Additional informational checks
        self.print_additional_info()

    def print_additional_info(self):
        """Print additional informational statistics"""
        print("\n=== Additional Information ===")

        # Check readers completion
        reader_pattern = r"Reader (\d+) completed (\d+)/20 iterations"
        reader_matches = re.findall(reader_pattern, self.output)
        for reader_id, completed in reader_matches:
            print(f"Reader {reader_id}: {completed}/20 iterations")

        # Check writers completion
        writer_pattern = r"Writer (\d+) completed (\d+)/20 iterations"
        writer_matches = re.findall(writer_pattern, self.output)
        for writer_id, completed in writer_matches:
            print(f"Writer {writer_id}: {completed}/20 iterations")

        # Check final counter value
        counter_match = re.search(r"Final value of shared_data: (\d+)", self.output)
        if counter_match:
            final_value = int(counter_match.group(1))
            print(f"Final counter value: {final_value}")

    def print_summary(self):
        """Print test summary report"""
        print("\n=== Test Summary ===")
        print(f"Total tests:  {self.test_count}")
        print(f"Passed:       {self.passed_count}")
        print(f"Failed:       {self.failed_count}")
        if self.test_count > 0:
            print(f"Success rate: {self.passed_count/self.test_count*100:.1f}%")
        else:
            print("Success rate: N/A")

        if self.failed_count == 0:
            print("\nFINAL RESULT: ALL TESTS PASSED")
            return 0
        else:
            print("\nFINAL RESULT: SOME TESTS FAILED")
            return 1

    def run_all_tests(self):
        """Execute all userspace program tests"""
        try:
            self.test_program_execution()
            return self.print_summary()
        except Exception as e:
            print(f"\n[!] Test error: {e}")
            import traceback

            traceback.print_exc()

            # Save debug info
            with open("userspace_failure.log", "w") as f:
                f.write(self.output)
            print("Debug info saved to userspace_failure.log")

            return 1
