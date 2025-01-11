"""Sound management for the game."""
import pygame
import os
from typing import Dict
from src.core.constants import AUDIO_VOLUMES

class SoundManager:
    """Manages game audio including sound effects and music."""
    
    def __init__(self):
        """Initialize the sound manager."""
        pygame.mixer.init()
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.volumes = AUDIO_VOLUMES.copy()
        
        # Load sound effects
        sound_dir = os.path.join('assets', 'sounds')
        self._load_sound('thrust', os.path.join(sound_dir, 'thrust.wav'))
        self._load_sound('shoot', os.path.join(sound_dir, 'shoot.wav'))
        self._load_sound('explosion_large', os.path.join(sound_dir, 'explosion_large.wav'))
        self._load_sound('explosion_medium', os.path.join(sound_dir, 'explosion_medium.wav'))
        self._load_sound('explosion_small', os.path.join(sound_dir, 'explosion_small.wav'))
        self._load_sound('game_over', os.path.join(sound_dir, 'game_over.wav'))
        self._load_sound('level_complete', os.path.join(sound_dir, 'level_complete.wav'))
        
        # Set volumes
        self.set_volume('sfx', self.volumes['sfx'])
    
    def _load_sound(self, name: str, path: str) -> None:
        """Load a sound effect.
        
        Args:
            name: Name to reference the sound by
            path: Path to the sound file
        """
        try:
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
                print(f"Loaded sound: {name}")  # Debug info
            else:
                print(f"Sound file not found: {path}")  # Debug info
        except Exception as e:
            print(f"Error loading sound {name}: {e}")  # Debug info
    
    def play_sound(self, name: str) -> None:
        """Play a sound effect.
        
        Args:
            name: Name of the sound to play
        """
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"Error playing sound {name}: {e}")  # Debug info
    
    def set_volume(self, category: str, volume: float) -> None:
        """Set volume for a category of sounds.
        
        Args:
            category: Category of sound ('sfx' or 'music')
            volume: Volume level (0.0 to 1.0)
        """
        self.volumes[category] = max(0.0, min(1.0, volume))
        
        if category == 'sfx':
            for sound in self.sounds.values():
                sound.set_volume(self.volumes['sfx'])
    
    def stop_all(self) -> None:
        """Stop all currently playing sounds."""
        pygame.mixer.stop() 