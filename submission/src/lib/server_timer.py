#!/usr/bin/env python3
"""
server_timer.py - Server-side timing and logging utility for FHE benchmark
"""
import time
import os
from datetime import datetime


class ServerTimer:
    """
    Timer utility for server-side logging with the expected format.
    
    The harness expects server logs in this format:
    HH:MM:SS [server] <step_number>: <description> completed (elapsed <X>s)
    """
    
    # ANSI color codes
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    def __init__(self):
        """Initialize the timer."""
        self.last_time = time.time()
        self.start_time = self.last_time
        # Check if we're in a terminal that supports colors
        self.use_colors = os.isatty(1)  # stdout is a terminal
    
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
        
        # Format server tag with color for better visibility
        if self.use_colors:
            server_tag = f"{self.GREEN}{self.BOLD}[server]{self.RESET}"
        else:
            server_tag = "[server]"
        
        if elapsed > 0:
            print(f"{timestamp} {server_tag} {num}: {name} completed (elapsed {int(elapsed)}s)")
        else:
            print(f"{timestamp} {server_tag} {num}: {name} completed")
        
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
