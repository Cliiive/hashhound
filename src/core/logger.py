import logging
from rich.logging import RichHandler

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._logger = None
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self, debug_mode=False):
        """Setup the logger with RichHandler."""
        level = logging.DEBUG if debug_mode else logging.INFO
        
        # Create logger
        self._logger = logging.getLogger("HashHound")
        self._logger.setLevel(level)
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Add RichHandler
        handler = RichHandler()
        handler.setLevel(level)
        
        # Set format
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        
        self._logger.addHandler(handler)
    
    def set_debug_mode(self, debug_mode=True):
        """Enable or disable debug mode."""
        level = logging.DEBUG if debug_mode else logging.INFO
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)
    
    def get_logger(self):
        """Get the logger instance."""
        return self._logger
    
    def info(self, message):
        """Log info message."""
        self._logger.info(message)
    
    def debug(self, message):
        """Log debug message."""
        self._logger.debug(message)
    
    def error(self, message):
        """Log error message."""
        self._logger.error(message)
    
    def warning(self, message):
        """Log warning message."""
        self._logger.warning(message)

# Convenience function to get logger instance
def get_logger():
    """Get the singleton logger instance."""
    return Logger()
