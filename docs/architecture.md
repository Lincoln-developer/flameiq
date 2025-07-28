# 🔥 FlameIQ – Architecture Overview

**FlameIQ** is an open-source CLI-based Python performance profiler that enables developers to analyze their scripts or applications through terminal commands, collect performance traces, and generate insightful flamegraphs for visualization.

This document describes the **architecture** of the FlameIQ CLI Profiler, outlining both the **high-level system flow** and **detailed internal components**.

---

## 📊 High-Level System Flow
# 🔥 FlameIQ – Architecture Overview

**FlameIQ** is an open-source CLI-based Python performance profiler that enables developers to analyze their scripts or applications through terminal commands, collect performance traces, and generate insightful flamegraphs for visualization.

This document describes the **architecture** of the FlameIQ CLI Profiler, outlining both the **high-level system flow** and **detailed internal components**.

---

## 📊 High-Level System Flow

```text
┌────────────────────────┐
│  Terminal / CLI Input  │
└────────────┬───────────┘
             ▼
┌─────────────────────┐
│     CLI Interface    │  ← [typer-based commands]
└────────┬────────────┘
         ▼
┌───────────────────────────────┐
│         Profiler Engine       │  ← [sampling + stack capture]
└────────────┬──────────────────┘
             ▼
┌─────────────────────┐
│   Trace Collector   │  ← [raw trace events, stack frames]
└────────┬────────────┘
         ▼
┌──────────────────────────┐
│   Flamegraph Formatter   │  ← [collapsed stacks or JSON]
└────────────┬─────────────┘
             ▼
┌────────────────────┐
│  Flamegraph Output  │ ← [SVG / HTML / JSON]
└────────────────────┘
```

# 🧱 FlameIQ – Detailed Internal Component Architecture

FlameIQ is built upon the following architectural principles to ensure maintainability, extensibility, and robustness:

Modularity: Each core component (CLI, Orchestrator, Sampler, Collector, Formatter, Exporter) has a clearly defined responsibility, minimizing inter-dependencies and allowing for independent development and testing.

Separation of Concerns: Different functionalities, such as user interaction, data collection, data aggregation, data formatting, and output handling, are strictly separated into distinct modules.

Performance First: The engine components are designed for efficiency, particularly the sampler and collector, to minimize profiling overhead on the target application.

Extensibility: The architecture is designed to easily integrate new profiling engines (e.g., for different profiling methods), additional output formats, or alternative visualization tools in the future.

Configuration Driven: Profiling parameters and output preferences are managed through a central configuration, enabling flexible and powerful user control.

## 🧩 Detailed Component Breakdown

### 1. `cli.py` – Command Line Interface (User Interface)
This module is the user's primary interaction point with FlameIQ. It's responsible for interpreting user commands and validating inputs.

`Role`: User interaction, command parsing, argument validation.

**Key Responsibilities**:

- Implements the CLI using libraries like Typer or argparse.
- Parses terminal commands (e.g., flameiq profile script.py --duration 10).
- Provides help messages, version information, and robust argument validation.
- Assembles a configuration object from user inputs and default settings.

**Data Flow**:

- `Input`: Raw terminal command strings and arguments.

- `Output`: A validated, structured configuration object passed to runner.py.

### 2. runner.py – Orchestrator
The "brain" of the profiling session, runner.py coordinates the lifecycle of the entire profiling process based on the user's configuration.

`Role`: Session management, component coordination, configuration application.

**Key Responsibilities**:

- Initializes and manages the lifecycle of sampler, collector, formatter, and exporter instances.
- Applies user-defined configurations (e.g., profiling duration, sampling rate, output format).
- Starts the profiling process, monitors its duration, and signals components to stop.
- Handles the sequential flow of data between the engine, formatter, and output layers.

**Data Flow**:

`Input`: Configuration object from cli.py.

`Output`:

- Control signals and specific parameters to engine/sampler.py (e.g., "start sampling for X seconds").
- Initiates the data flow by connecting the sampler to the collector.
- Triggers formatting by passing aggregated data to formatter/flamegraph.py.
- Triggers output by passing formatted data to output/exporter.py.

### 3. engine/sampler.py – Sampling Profiler
This module is at the heart of performance data collection, responsible for capturing the application's state at regular intervals.

`Role`: Raw performance data collection (sampling).

**Key Responsibilities**:

- Periodically samples the call stacks of all active Python threads in the target application.
- Utilizes low-level Python introspection (e.g., sys._current_frames()) to fetch current stack frames.
- Converts raw frame objects into structured call stack representations (e.g., lists of (filename, lineno, function_name)).
- Operates in a separate background thread or asyncio task to minimize interference with the profiled application.
- Supports configurable sampling rates and maximum profiling durations.

**Data Flow**:

`Input`: Implicitly, the execution state of the profiled Python application; configuration from runner.py (sampling rate, duration).

`Output`: A continuous stream of raw stack traces (each representing a snapshot of a thread's call stack at a specific time) sent to engine/collector.py.

### 4. engine/collector.py – Trace Collector
The collector aggregates and organizes the raw samples into a meaningful structure, preparing them for visualization.

`Role`: Trace aggregation and data consolidation.

**Key Responsibilities**:

- Consumes the stream of raw stack traces from engine/sampler.py.
- Deduplicates identical call stacks to save memory and processing time.
- Aggregates sample counts for performance hotspots, effectively counting how many times each unique call path was observed.
- Stores the aggregated trace data in a memory-efficient structure optimized for high-frequency sampling (e.g., a tree-like structure or a dictionary of tuples).

**Data Flow**:

`Input`: Stream of raw stack traces from engine/sampler.py.

`Output`: Aggregated trace data (e.g., a dictionary or tree where keys are call stacks and values are their accumulated counts) passed to formatter/flamegraph.py.

### 5. formatter/flamegraph.py – Formatter
This module translates the aggregated performance data into specific output formats consumable by visualization tools.

`Role`: Data transformation for visualization.

**Key Responsibilities**:

- Converts the aggregated trace data into various standard formats.
- Supports Collapsed Stack Format (for Brendan Gregg's flamegraph.pl), which is a plain text file where each line represents a call stack and its count (e.g., main;funcA;funcB 123).
- Supports JSON Format (for tools like Speedscope.io), which typically represents the call tree as nested JSON objects.
- (Planned) Native HTML/SVG output for direct browser visualization without external tools.
- Normalizes function names and encodes special characters to ensure compatibility with target formats.

**Data Flow**:

`Input`: Aggregated trace data from engine/collector.py; desired output format from runner.py.

`Output`: A formatted string (for collapsed format) or a JSON-serializable object (for Speedscope) passed to output/exporter.py.

### 6. output/exporter.py – Output Handler
The final step in the pipeline, the exporter is responsible for persisting the formatted data and facilitating visualization.

`Role`: File I/O and visualization launch.

**Key Responsibilities**:

- Writes the formatted output data to disk (e.g., .txt, .json, .html).
-Automatically generates unique filenames, often incorporating timestamps and metadata.
- Supports optional compression of output files (e.g., .gz).
- (Optional) Automatically launches the generated flamegraph in the user's default web browser after the profiling session concludes.

**Data Flow**:

`Input`: Formatted output data (string or JSON object) from formatter/flamegraph.py; output path and launch options from runner.py.

`Output`:
- A persisted file on the user's disk containing the profiling results.
- A launched web browser window displaying the visualization (if configured).