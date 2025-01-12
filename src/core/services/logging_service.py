"""Logging service for runtime logs."""
from typing import Optional
import os
from datetime import datetime

class LoggingService:
    """Service for managing runtime logs.
    
    Provides:
    - Runtime log creation and management
    - Error logging
    - Service state logging
    """
    
    _instance = None
    
    def __new__(cls):
        """Create or return singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        """Initialize the logging service."""
        if self._initialized:
            return
            
        self._log_dir = "logs/runtime"
        self._current_log = None
        self._initialized = True
        
        # Ensure log directory exists
        os.makedirs(self._log_dir, exist_ok=True)
        
        # Create new log file for this session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_log = os.path.join(self._log_dir, f"game_log_{timestamp}.txt")
        
        with open(self._current_log, 'w') as f:
            f.write(f"=== Game Session Log {timestamp} ===\n\n")
            
        print(f"LoggingService initialized - Log file: {self._current_log}")
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message.
        
        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        with open(self._current_log, 'a') as f:
            f.write(log_entry)
            
    def get_current_log(self) -> Optional[str]:
        """Get path to current log file.
        
        Returns:
            Path to current log file or None
        """
        return self._current_log
        
    def cleanup(self) -> None:
        """Clean up the logging service."""
        if self._current_log:
            self.log("=== End of Session ===")
        print("LoggingService cleaned up") 