#!/usr/bin/env python3
"""
server_timer.py - Server-side timing and logging utility for FHE benchmark
"""
import time
from datetime import datetime


class ServerTimer:
    """
    Timer utility for server-side logging with the expected format.
    
    The harness expects server logs in this format:
    HH:MM:SS [server] <step_number>: <description> completed (elapsed <X>s)
    """
    
    def __init__(self):
        """Initialize the timer."""
        self.last_time = time.time()
        self.start_time = self.last_time
    
    def log_step(self, num, name):
        """
        Log a server step with the expected format.
        
        Args:
            num: Step number (e.g., 0, 1, 2, etc.)
            name: Step description (e.g., "Loading keys", "Matrix-vector product")
        """
        current = time.time()
        elapsed = current - self.last_time
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if elapsed > 0:
            print(f"{timestamp} [server] {num}: {name} completed (elapsed {int(elapsed)}s)")
        else:
            print(f"{timestamp} [server] {num}: {name} completed")
        
        # Ensure output is immediately visible
        import sys
        sys.stdout.flush()
        
        self.last_time = current
    
    def get_total_elapsed(self):
        """
        Get total elapsed time since timer creation.
        
        Returns:
            float: Total elapsed seconds
        """
        return time.time() - self.start_time
