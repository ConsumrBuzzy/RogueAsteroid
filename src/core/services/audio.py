"""Audio manager for game sounds."""
import pygame
import os

class AudioManager:
    """Manages game audio."""
    
    def __init__(self):
        """Initialize the audio manager."""
        self.enabled = False  # Default to sound off
        self.sounds = {}  # Dictionary to store loaded sounds
    
    def toggle_sound(self):
        """Toggle sound on/off."""
        self.enabled = not self.enabled
        print(f"Sound {'enabled' if self.enabled else 'disabled'}")  # Debug info
    
    def play_shoot(self):
        """Play shoot sound."""
        if not self.enabled:
            return
    
    def play_explosion(self, size='medium'):
        """Play explosion sound."""
        if not self.enabled:
            return
    
    def play_thrust(self):
        """Play thrust sound."""
        if not self.enabled:
            return
    
    def stop_all(self):
        """Stop all playing sounds."""
        pygame.mixer.stop() 