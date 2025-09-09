#!/usr/bin/env python3
"""
server_logger.py - Consistent server-style logging utility
"""
import os
import sys
from datetime import datetime


class ServerLogger:
    """Simple server-style logger for consistent formatting."""
    
    # ANSI color codes
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    def __init__(self):
        # Check if we're in a terminal that supports colors
        self.use_colors = os.isatty(sys.stdout.fileno())
    
    def print(self, message):
        """
        Print a message with server format: HH:MM:SS [server] message
        
        Args:
            message: Message to print
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format server tag with color
        if self.use_colors:
            server_tag = f"{self.GREEN}{self.BOLD}[server]{self.RESET}"
        else:
            server_tag = "[server]"
        
        print(f"{timestamp} {server_tag} {message}")
        sys.stdout.flush()


# Global instance for easy import
server_logger = ServerLogger()


def server_print(message):
    """Convenience function for server-style printing."""
    server_logger.print(message)