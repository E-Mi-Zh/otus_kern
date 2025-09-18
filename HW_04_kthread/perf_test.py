#!/usr/bin/env python3
import os
import shutil
import sys
import subprocess
import time
import json
import matplotlib.pyplot as plt
from datetime import datetime


class PerfComparator:
    def __init__(self, kernel_module, userspace_program):
        self.kernel_module = kernel_module
        self.userspace_program = userspace_program
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = f"perf_results_{self.timestamp}"

    def run_command(self, cmd, check=True):
        """Execute shell command - cmd can be string (for shell=True) or list"""
        if isinstance(cmd, str):
            # Use shell for string commands with shell=True
            result = subprocess.run(
                cmd,
                shell=True,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        else:  # Use list for direct command execution
            result = subprocess.run(
                cmd,
                shell=False,
                check=check,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        return result.stdout, result.stderr, result.returncode

    def setup_environment(self):
        """Create results directory"""
        os.makedirs(self.results_dir, exist_ok=True)
        print(f"[+] Results will be saved in: {self.results_dir}")

        # Check if perf is available
        if not shutil.which("perf"):
            print(
                "[!] Error: perf not found. Install with: sudo apt install linux-perf"
            )
            return False
        return True

    def test_kernel_module(self):
        """Run perf on kernel module"""
        print("\n=== Testing Kernel Module ===")

        # Load module
        print("[+] Loading kernel module...")
        stdout, stderr, returncode = self.run_command(
            ["sudo", "modprobe", self.kernel_module], check=False
        )
        time.sleep(0.5)

        # Run perf record
        print("[+] Running perf record on kernel module...")
        perf_data = f"{self.results_dir}/perf_rw_kern.data"
        self.run_command(
            [
                "sudo",
                "perf",
                "record",
                "-e",
                "cycles",
                "-g",
                "-o",
                perf_data,
                "--",
                "sleep",
                "3",
            ]
        )

        # Generate report
        print("[+] Generating perf report...")
        perf_report = f"{self.results_dir}/perf_rw_kern.log"
        try:
            with open(perf_report, "w") as f:
                subprocess.run(
                    ["sudo", "perf", "report", "-i", perf_data, "--stdio"],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
        except Exception as e:
            print(f"[!] Error generating perf report: {e}")

        # Generate flamegraph in a separate step to avoid issues

        # Unload module
        print("[+] Unloading kernel module...")
        self.run_command(["sudo", "rmmod", self.kernel_module])

        return perf_report

    def test_userspace_program(self):
        """Run perf on userspace program"""
        print("\n=== Testing Userspace Program ===")

        # Check if program exists with ./ prefix
        program_path = self.userspace_program
        if not os.path.exists(program_path):
            program_path = f"./{self.userspace_program}"
            if not os.path.exists(program_path):
                print(f"[!] Error: Program {self.userspace_program} not found")
                return None

        # Run perf record
        print("[+] Running perf record on userspace program...")
        perf_data = f"{self.results_dir}/perf_app_us.data"
        self.run_command(
            [
                "perf",
                "record",
                "-e",
                "cycles",
                "-g",
                "--call-graph",
                "dwarf",
                "-o",
                perf_data,
                "--",
                f"./{program_path}",
            ]
        )

        # Generate report
        print("[+] Generating perf report...")
        perf_report = f"{self.results_dir}/perf_app_us.log"
        try:
            with open(perf_report, "w") as f:
                subprocess.run(
                    ["perf", "report", "-i", perf_data, "--stdio"],
                    stdout=f,
                    stderr=subprocess.DEVNULL,  # Suppress stderr
                    check=False,
                )
        except Exception as e:
            print(f"[!] Error generating perf report: {e}")

        return perf_report

    def generate_flamegraph(self, perf_data, output_prefix):
        """Generate flamegraph from perf data"""
        try:
            # Generate folded stacks
            folded_file = f"{output_prefix}.folded"
            try:
                with open(folded_file, "w") as f:
                    perf_script = subprocess.Popen(
                        ["sudo", "perf", "script", "-i", perf_data],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    stackcollapse = subprocess.run(
                        [
                            shutil.which("stackcollapse-perf.pl")
                            or "stackcollapse-perf.pl"
                        ],
                        stdin=perf_script.stdout,
                        stdout=f,
                        stderr=subprocess.PIPE,
                    )
                    perf_script.wait()
            except FileNotFoundError:
                print("[!] stackcollapse-perf.pl not found. Install flamegraph tools.")
                return None

            # Generate flamegraph
            flamegraph_file = f"{output_prefix}.html"
            subprocess.run(
                [shutil.which("flamegraph.pl") or "flamegraph.pl", folded_file],
                stdout=open(flamegraph_file, "w"),
            )

            print(f"[+] Flamegraph saved: {flamegraph_file}")
            return flamegraph_file
        except Exception as e:
            print(f"[!] Flamegraph generation failed: {e}")
            return None

    def parse_perf_report(self, report_file):
        """Parse perf report to extract cycle counts"""
        cycles = 0
        found_cycles = False
        try:
            with open(report_file, "r") as f:
                content = f.read()

            # Perf report --stdio format has samples and cycles in specific lines
            lines = content.split("\n")
            for line in lines:
                # Look for lines with samples and cycle counts
                if "Samples:" in line and "cycles" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "cycles" in part.lower() and i > 0:
                            # Get the number before "cycles"
                            cycle_str = parts[i - 1].replace(",", "")
                            if cycle_str.isdigit():
                                cycles = int(cycle_str)
                                found_cycles = True
                                break

                # Alternative format: look for event counts
                elif "Event count" in line and "cycles" in line.lower():
                    parts = line.split(":")
                    if len(parts) > 1:
                        cycle_str = parts[1].strip().split()[0].replace(",", "")
                        if cycle_str.isdigit():
                            cycles = int(cycle_str)
                            found_cycles = True
                            break

            # If no cycles found, try to find any large number that might be cycles
            if not found_cycles:
                for line in lines:
                    if any(
                        word.isdigit() and len(word.replace(",", "")) > 6
                        for word in line.split()
                    ):
                        for word in line.split():
                            if (
                                word.replace(",", "").isdigit()
                                and len(word.replace(",", "")) > 6
                            ):
                                cycles = int(word.replace(",", ""))
                                found_cycles = True
                                break
                        if found_cycles:
                            break

            if not found_cycles:
                print(f"[!] Warning: Could not find cycle counts in {report_file}")
                print("    Please check the perf report format manually")

            return cycles
        except Exception as e:
            print(f"[!] Error parsing perf report: {e}")
            return 0

    def compare_performance(self):
        """Compare performance between kernel and userspace"""
        print("\n=== Performance Comparison ===")

        # Run tests
        kern_report = self.test_kernel_module()
        us_report = self.test_userspace_program()

        if not kern_report or not us_report:
            print("[!] Performance comparison failed")
            return

        # Generate flamegraphs after main tests
        print("[+] Generating flamegraphs...")
        self.generate_flamegraph(
            f"{self.results_dir}/perf_rw_kern.data", f"{self.results_dir}/flg_kern"
        )
        self.generate_flamegraph(
            f"{self.results_dir}/perf_app_us.data", f"{self.results_dir}/flg_us"
        )

        # Parse results
        kern_cycles = self.parse_perf_report(kern_report)
        us_cycles = self.parse_perf_report(us_report)

        print(f"\n[+] Kernel cycles: {kern_cycles:,}")
        print(f"[+] Userspace cycles: {us_cycles:,}")

        if kern_cycles > 0 and us_cycles > 0:
            ratio = us_cycles / kern_cycles
            print(f"[+] Ratio (Userspace/Kernel): {ratio:.2f}x")

            # Create comparison chart
            self.create_comparison_chart(kern_cycles, us_cycles)

        print(f"\n[+] Results saved in: {self.results_dir}")

    def create_comparison_chart(self, kern_cycles, us_cycles):
        """Create performance comparison chart"""
        labels = ["Kernel", "Userspace"]
        cycles = [kern_cycles, us_cycles]

        plt.figure(figsize=(10, 6))

        # Bar chart
        plt.subplot(1, 2, 1)
        bars = plt.bar(labels, cycles, color=["blue", "orange"])
        plt.ylabel("CPU Cycles")
        plt.title("CPU Cycles Comparison")

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:,}",
                ha="center",
                va="bottom",
            )

        # Ratio chart
        plt.subplot(1, 2, 2)
        ratio = us_cycles / kern_cycles
        plt.bar(["Ratio"], [ratio], color="green")
        plt.ylabel("Userspace/Kernel Ratio")
        plt.title(f"Performance Ratio: {ratio:.2f}x")

        plt.tight_layout()
        chart_path = f"{self.results_dir}/performance_comparison.png"
        plt.savefig(chart_path)
        plt.close()

        print(f"[+] Comparison chart saved: {chart_path}")

    def run_comparison(self):
        """Main comparison runner"""
        if self.setup_environment():
            self.compare_performance()


def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python perf_comparison.py <kernel_module> <userspace_program>")
        print("Example: python perf_comparison.py rw_kern rw_us")
        return 1

    kernel_module = sys.argv[1]
    userspace_program = sys.argv[2]

    comparator = PerfComparator(kernel_module, userspace_program)
    comparator.run_comparison()


if __name__ == "__main__":
    main()
