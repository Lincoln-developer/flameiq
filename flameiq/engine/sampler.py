"""
A pure Python-based sampler prototype for FlameIQ.

This module demonstrates the core concept of sampling call stacks
using Python's native introspection tools. It runs in a separate
thread and periodically captures the stack frames of all active
threads in the profiled process.

Note: This is a prototype for educational purposes and will be replaced
by a high-performance C extension for the final product.
"""

import sys
import threading
import time
import os
import signal
from collections import defaultdict
from typing import List, Dict, Any, Optional

class Sampler:
    """
    A simple, thread-based sampler to capture Python stack frames.
    """
    def __init__(self, sampling_rate_hz: int, collector: 'Collector'):
        """
        Initializes the sampler with a sampling rate and a collector instance.

        Args:
            sampling_rate_hz (int): The frequency at which to sample the stacks.
            collector (Collector): An instance of the collector to push samples to.
        """
        self._interval_s = 1.0 / sampling_rate_hz
        self._stop_event = threading.Event()
        self._thread = None
        self._collector = collector

    def start(self):
        """
        Starts the background thread for sampling.
        """
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Signals the sampling thread to stop gracefully.
        """
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def _run(self):
        """
        The main sampling loop. Runs in a separate thread.
        """
        while not self._stop_event.is_set():
            # Get a snapshot of all current threads' stacks
            frames = sys._current_frames()
            
            # Process each thread's stack
            for thread_id, frame in frames.items():
                stack = self._get_stack_from_frame(frame)
                if stack:
                    self._collector.add_sample(stack)
            
            # Wait for the next sampling interval or stop signal
            self._stop_event.wait(self._interval_s)

    def _get_stack_from_frame(self, frame: Any) -> List[Dict[str, Any]]:
        """
        Walks up the stack from a given frame object and returns a list of frames.
        """
        stack = []
        while frame:
            stack.append({
                "function": frame.f_code.co_name,
                "file": os.path.basename(frame.f_code.co_filename),
                "lineno": frame.f_lineno,
            })
            frame = frame.f_back
        # We reverse the stack so it goes from the top of the call tree down to the current frame
        return stack[::-1]
