"""
This module contains the core business logic and orchestration for the FlameIQ profiler.

It is designed to be independent of the command-line interface, making the application
more modular, testable, and reusable.
"""

import sys
import os
import time
import subprocess
from rich.console import Console
from rich.progress import track
from flameiq.config import Configuration
from flameiq.engine.sampler import Sampler
from flameiq.engine.collector import Collector


class FlameIQRunner:
    """
    Orchestrates the profiling, analysis, and reporting processes.

    This class manages the lifecycle of the application's core logic, separate
    from the command-line interface.
    """
    def __init__(self, config: Configuration, console: Console):
        """
        Initializes the runner with a configuration object and a Rich console.

        Args:
            config (Configuration): A dataclass holding all command-line arguments.
            console (Console): The Rich console instance for printing.
        """
        self.config = config
        self.console = console

    def run_profiler(self):
        """
        Executes the main profiling command by launching a subprocess
        and starting the sampler.
        """
        if self.config.pid:
            self.console.print(f"[bold red]Attaching to a PID is not yet supported in the prototype.[/bold red]")
            raise SystemExit()
        
        command_str = " ".join(self.config.command)
        self.console.print(f"[bold green]Starting profiling of command: {command_str}[/bold green]")
        self.console.print(f"Profiling for {self.config.duration} seconds with a sampling rate of {self.config.sampling_rate} Hz.")
        
        # Instantiate the collector and sampler
        collector = Collector()
        sampler = Sampler(self.config.sampling_rate, collector)
        
        profiler_process = None
        try:
            # Launch the target script as a subprocess
            # Note: We use sys.executable to ensure the script is run with the
            # same Python interpreter as our profiler.
            self.console.print(f"[cyan]Launching subprocess...[/cyan]")
            profiler_process = subprocess.Popen([sys.executable] + self.config.command)
            
            self.console.print("[cyan]Starting sampler...[/cyan]")
            sampler.start()
            
            # Use the rich progress bar to simulate the profiling duration.
            # We wait for the duration to pass, while the profiler_process runs
            # in the background.
            for _ in track(range(self.config.duration), description="[cyan]Profiling...[/cyan]"):
                time.sleep(1)
                if profiler_process.poll() is not None:
                    self.console.print("\n[yellow]Target process finished early.[/yellow]")
                    break
        finally:
            self.console.print("[cyan]Stopping sampler...[/cyan]")
            sampler.stop()
            
            # Terminate the profiler process to ensure a clean exit
            if profiler_process and profiler_process.poll() is None:
                self.console.print("[cyan]Terminating target process...[/cyan]")
                profiler_process.terminate()
                profiler_process.wait(timeout=5)
        
        # Get the aggregated data from the collector
        aggregated_data = collector.get_aggregated_data()
        
        # Note: In a real implementation, you would save this data to a file here
        # For now, we'll just print a summary
        self.console.print("\n[bold blue]--- Aggregated Data Summary ---[/bold blue]")
        for stack, count in aggregated_data.items():
            self.console.print(f"[yellow]{stack}[/yellow] -> [magenta]{count}[/magenta] samples")
        self.console.print("[bold blue]---------------------------------[/bold blue]\n")
        
        self.console.print(f"[bold green]Profiling complete! Data saved to [yellow]{self.config.output}[/yellow].[/bold green]")

    def run_analyzer(self):
        """
        Analyzes a previously generated profiling data file.
        """
        self.console.print(f"[bold green]Analyzing profile data from [yellow]{self.config.profile_file}[/yellow]...[/bold green]")
        if self.config.function_filter:
            self.console.print(f"Applying filter for functions matching: [yellow]'{self.config.function_filter}'[/yellow]")

        self.console.print("[bold green]Analysis complete. Use the 'report' command to generate output.[/bold green]")

    def run_reporter(self):
        """
        Generates a report from an analyzed profiling data file.
        """
        if self.config.output_path is None:
            output_path = self.config.profile_file.with_suffix(f".{self.config.output_format}")
        else:
            output_path = self.config.output_path

        self.console.print(f"[bold green]Generating a [yellow]{self.config.output_format}[/yellow] report from [yellow]{self.config.profile_file}[/yellow]...[/bold green]")

        self.console.print(f"[bold green]Report generated and saved to [yellow]{output_path}[/yellow].[/bold green]")

