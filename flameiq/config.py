from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class Configuration:
    """A data class to hold all configuration options for a profiling session."""
    command: Optional[List[str]] = None
    pid: Optional[int] = None
    duration: int = 10
    sampling_rate: int = 99
    output: Path = Path("profile.flameiq")
    # For analyze/report
    profile_file: Optional[Path] = None
    function_filter: Optional[str] = None
    output_format: Optional[str] = None
    output_path: Optional[Path] = None