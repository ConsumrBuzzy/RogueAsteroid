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
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set up current session log
        current_handler = logging.FileHandler(os.path.join(self.logs_dir, 'current_session.log'), mode='w')
        current_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(current_handler)
        
        # Set up historical log with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        historical_handler = logging.FileHandler(
            os.path.join(self.logs_dir, f'game_log_{timestamp}.log'), mode='w'
        )
        historical_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(historical_handler)
        
        # Optional console output for debugging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)

# Global logger instance
_logger: Optional[GameLogger] = None

def get_logger() -> GameLogger:
    """Get or create the global logger instance."""
    global _logger
    if _logger is None:
        _logger = GameLogger()
    return _logger 