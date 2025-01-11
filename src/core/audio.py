"""Audio system for managing sound effects."""
import os
import pygame
from typing import Dict, Optional

class AudioManager:
    """Manages loading and playing of sound effects."""
    
    def __init__(self):
        pygame.mixer.init()
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # Load sound effects
        self._load_sounds()
    
    def _load_sounds(self) -> None:
        """Load all sound effects from assets directory."""
        sounds_dir = os.path.join('assets', 'sounds')
        
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion_large': 'explosion_large.wav',
            'explosion_medium': 'explosion_medium.wav',
            'explosion_small': 'explosion_small.wav',
            'thrust': 'thrust.wav',
        }
        
        for name, filename in sound_files.items():
            path = os.path.join(sounds_dir, filename)
            try:
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
            except pygame.error:
                print(f"Warning: Could not load sound '{filename}'")
    
    def play_sound(self, name: str, loop: bool = False) -> Optional[pygame.mixer.Channel]:
        """Play a sound effect by name."""
        if name not in self.sounds:
            return None
            
        sound = self.sounds[name]
        sound.set_volume(self.sfx_volume)
        
        channel = sound.play(-1 if loop else 0)
        return channel
    
    def stop_sound(self, name: str) -> None:
        """Stop a specific sound from playing."""
        if name in self.sounds:
            self.sounds[name].stop()
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def play_explosion(self, size: str) -> None:
        """Play appropriate explosion sound based on asteroid size."""
        sound_name = f'explosion_{size}'
        self.play_sound(sound_name) 