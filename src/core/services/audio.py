"""Audio manager for game sounds."""
import pygame
import os

class AudioManager:
    """Manages game audio and sound effects."""
    
    def __init__(self):
        """Initialize the audio manager."""
        self.sounds = {}
        self._load_sounds()
        
    def _load_sounds(self):
        """Load all game sounds."""
        sound_dir = os.path.join('assets', 'sounds')
        
        # Create sounds directory if it doesn't exist
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
            print(f"Created sounds directory at {sound_dir}")
        
        # Define sound files to load
        sound_files = {
            'shoot': 'shoot.wav',
            'explosion_small': 'explosion_small.wav',
            'explosion_medium': 'explosion_medium.wav',
            'explosion_large': 'explosion_large.wav',
            'thrust': 'thrust.wav'
        }
        
        # Load each sound if file exists
        for name, filename in sound_files.items():
            path = os.path.join(sound_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    print(f"Loaded sound: {name}")
                except pygame.error as e:
                    print(f"Error loading sound {name}: {e}")
            else:
                print(f"Sound file not found: {path}")
    
    def play_shoot(self):
        """Play shoot sound effect."""
        if 'shoot' in self.sounds:
            self.sounds['shoot'].play()
    
    def play_explosion(self, size='medium'):
        """Play explosion sound effect.
        
        Args:
            size: Size of explosion ('small', 'medium', 'large')
        """
        sound_name = f'explosion_{size}'
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_thrust(self):
        """Play thrust sound effect."""
        if 'thrust' in self.sounds:
            self.sounds['thrust'].play()
    
    def stop_all(self):
        """Stop all playing sounds."""
        pygame.mixer.stop() 