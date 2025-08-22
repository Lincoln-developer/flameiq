import sys
import os
import time
import toml
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt
from flameiq.runner import Configuration, FlameIQRunner

# --- Configuration & Setup ---

# Initialize the main Typer app and Rich console
app = typer.Typer(
    name="flameiq",
    help="FlameIQ: A powerful performance profiler for Python applications.",
    rich_help_panel="Help"
)
console = Console()

# Define the CLI version
__version__ = "0.1.0"

# Set up the configuration directory and file
CONFIG_DIR = Path(typer.get_app_dir("flameiq"))
CONFIG_FILE = CONFIG_DIR / "config.toml"

# Define the structure for the report output format
class OutputFormat(str, Enum):
    """Enum for valid output formats."""
    svg = "svg"
    json = "json"
    html = "html"
    text = "text"

# --- Main CLI Callbacks and Options ---

def _version_callback(value: bool):
    """Prints the application version and exits."""
    if value:
        console.print(f"[bold blue]FlameIQ CLI[/bold blue] v{__version__}")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        help="Show the application's version and exit.",
        is_eager=True,
    )
):
    """
    FlameIQ: A command-line profiler for Python.
    """
    # This is the main callback. If no subcommand is given,
    # the help message will be displayed automatically.
    pass

# --- Profiling Command Group ---

# The `profile` command is the heart of the CLI.
@app.command()
def profile(
    command: List[str] = typer.Argument(..., help="The Python command to profile (e.g., 'python my_script.py')."),
    pid: Optional[int] = typer.Option(
        None,
        "--pid",
        "-p",
        help="Attach to an existing process with the given PID.",
    ),
    duration: int = typer.Option(
        10,
        "--duration",
        "-d",
        help="The duration in seconds to profile the process.",
        min=1,
    ),
    sampling_rate: int = typer.Option(
        99,
        "--sampling-rate",
        "-s",
        help="The frequency (in Hz) at which to sample the process stack. Lower is less overhead.",
        min=1,
    ),
    output: Path = typer.Option(
        "profile.flameiq",
        "--output",
        "-o",
        help="The path to save the profiling data.",
    )
):
    """
    Run a performance profile on a command or an existing process.
    """
    # Create a Configuration object to pass all arguments to the runner
    config = Configuration(
        command=command,
        pid=pid,
        duration=duration,
        sampling_rate=sampling_rate,
        output=output
    )
    # Pass the config and console to the runner and execute the command
    runner = FlameIQRunner(config, console)
    runner.run_profiler()

# --- Analysis Command Group ---

@app.command()
def analyze(
    profile_file: Path = typer.Argument(..., exists=True, help="Path to the profile data file to analyze."),
    function_filter: Optional[str] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter the analysis to a specific function name or module.",
    )
):
    """
    Analyze a previously generated profile data file.
    """
    config = Configuration(
        profile_file=profile_file,
        function_filter=function_filter
    )
    runner = FlameIQRunner(config, console)
    runner.run_analyzer()

# --- Report Command Group ---

@app.command()
def report(
    profile_file: Path = typer.Argument(..., exists=True, help="Path to the profile data file to generate a report from."),
    output_format: OutputFormat = typer.Option(
        "svg",
        "--output-format",
        "-f",
        help="The format of the report to generate.",
    ),
    output_path: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="The path to save the generated report. Defaults to a filename based on the profile file."
    )
):
    """
    Generate a report from a profile data file in various formats.
    """
    config = Configuration(
        profile_file=profile_file,
        output_format=output_format.value,
        output_path=output_path
    )
    runner = FlameIQRunner(config, console)
    runner.run_reporter()

# --- Configuration Command Group ---

config_app = typer.Typer(
    name="config",
    help="Manage FlameIQ's configuration settings.",
)
app.add_typer(config_app, name="config")

@config_app.command("set")
def config_set(key: str, value: str):
    """
    Set a configuration value.
    Example: flameiq config set default-format svg
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_data = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            config_data = toml.load(f)
    
    config_data[key] = value
    
    with open(CONFIG_FILE, "w") as f:
        toml.dump(config_data, f)
        
    console.print(f"Configuration key '[yellow]{key}[/yellow]' set to '[yellow]{value}[/yellow]'.")

@config_app.command("show")
def config_show():
    """
    Display the current configuration.
    """
    if not CONFIG_FILE.exists():
        console.print("[yellow]No configuration file found.[/yellow]")
        return
        
    with open(CONFIG_FILE, "r") as f:
        config_data = toml.load(f)

    console.print("[bold blue]Current Configuration:[/bold blue]")
    for key, value in config_data.items():
        console.print(f"  [cyan]{key}[/cyan] = [yellow]{value}[/yellow]")


# --- Main Entry Point ---

if __name__ == "__main__":
    app()
