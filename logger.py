import logging
from typing import Optional
from pathlib import Path

class MCPLogger:
    """Logger class for MCP Adapter SDK components"""
    
    def __init__(self, 
                 name: str, 
                 debug_mode: bool = False, 
                 log_file: Optional[Path] = None):
        self.logger = logging.getLogger(name)
        self.debug_mode = debug_mode
        
        # Set base level based on debug mode
        base_level = logging.DEBUG if debug_mode else logging.INFO
        self.logger.setLevel(base_level)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
        )
        console_formatter = logging.Formatter(
            '[%(name)s][%(levelname)s] %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(base_level)
        self.logger.addHandler(console_handler)
        
        # File handler (if log_file specified)
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            self.logger.addHandler(file_handler)
    
    def log_debug(self, msg: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(msg, *args, **kwargs)
    
    def log_info(self, msg: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(msg, *args, **kwargs)
    
    def log_warning(self, msg: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(msg, *args, **kwargs)
    
    def log_error(self, msg: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(msg, *args, **kwargs)