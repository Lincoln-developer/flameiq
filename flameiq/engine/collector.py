from collections import defaultdict
from typing import List, Dict, Any

class Collector:
    """
    A simple collector that aggregates call stacks and their counts.
    """
    def __init__(self):
        self._data = defaultdict(int)

    def add_sample(self, stack: List[Dict[str, Any]]):
        """
        Adds a single call stack sample to the aggregated data.
        """
        # Create a simple string representation of the stack to use as a key
        stack_path = ';'.join([f"{f['file']}:{f['function']}" for f in stack])
        self._data[stack_path] += 1

    def get_aggregated_data(self) -> Dict[str, int]:
        """
        Returns the final aggregated data.
        """
        return dict(self._data)