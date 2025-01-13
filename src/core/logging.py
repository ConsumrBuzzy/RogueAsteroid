"""Game logging system."""
import os
import logging
from datetime import datetime
from typing import Optional

class GameLogger:
    """Handles game logging to both current and historical log files."""
    
    def __init__(self):
        """Initialize the logger."""
        self.logger = logging.getLogger('RogueAsteroid')
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        self.runtime_dir = os.path.join(self.logs_dir, 'runtime')
        os.makedirs(self.runtime_dir, exist_ok=True)
        
        # Set up current session log with more detailed formatting
        current_handler = logging.FileHandler(os.path.join(self.logs_dir, 'current_session.log'), mode='w')
        current_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)8s - %(filename)20s:%(lineno)4d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        current_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(current_handler)
        
        # Set up historical log with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        historical_handler = logging.FileHandler(
            os.path.join(self.runtime_dir, f'game_log_{timestamp}.log'), mode='w'
        )
        historical_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)8s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        historical_handler.setLevel(logging.INFO)  # Only log INFO and above for historical logs
        self.logger.addHandler(historical_handler)
        
        # Console output for debugging with minimal formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)8s - %(message)s'))
        console_handler.setLevel(logging.INFO)  # Only show INFO and above in console
        self.logger.addHandler(console_handler)
        
        # Log initial setup
        self.info("Logging system initialized")
        self.debug(f"Log directory: {self.logs_dir}")
        self.debug(f"Runtime logs directory: {self.runtime_dir}")
    
    def debug(self, message: str) -> None:
        """Log debug message - for detailed debugging information."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message - for general game events and state changes."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message - for concerning but non-fatal issues."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message - for recoverable errors."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message - for unrecoverable errors that require game shutdown."""
        self.logger.critical(message)

# Global logger instance
_logger: Optional[GameLogger] = None

def get_logger() -> GameLogger:
    """Get or create the global logger instance."""
    global _logger
    if _logger is None:
        _logger = GameLogger()
    return _logger 