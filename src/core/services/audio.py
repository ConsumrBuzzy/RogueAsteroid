"""Audio manager for game sounds."""
import pygame
import os
from src.core.logging import get_logger

class AudioManager:
    """Manages game audio."""
    
    def __init__(self):
        """Initialize the audio manager."""
        self.logger = get_logger()
        self.enabled = False  # Default to sound off
        self.sounds = {}  # Dictionary to store loaded sounds
        self.logger.info("Audio manager initialized (sound disabled by default)")
    
    def toggle_sound(self):
        """Toggle sound on/off."""
        self.enabled = not self.enabled
        self.logger.info(f"Sound {'enabled' if self.enabled else 'disabled'}")
    
    def play_shoot(self):
        """Play shoot sound."""
        if not self.enabled:
            self.logger.debug("Shoot sound skipped (audio disabled)")
            return
        self.logger.debug("Playing shoot sound")
    
    def play_explosion(self, size='medium'):
        """Play explosion sound."""
        if not self.enabled:
            self.logger.debug(f"Explosion sound skipped (audio disabled)")
            return
        self.logger.debug(f"Playing {size} explosion sound")
    
    def play_thrust(self):
        """Play thrust sound."""
        if not self.enabled:
            self.logger.debug("Thrust sound skipped (audio disabled)")
            return
        self.logger.debug("Playing thrust sound")
    
    def stop_all(self):
        """Stop all playing sounds."""
        pygame.mixer.stop()
        self.logger.debug("Stopped all sounds") 