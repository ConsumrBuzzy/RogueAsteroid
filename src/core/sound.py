"""Sound management for the game."""
import pygame
import os
import wave
import struct
import math
from typing import Dict, Tuple
from src.core.constants import AUDIO_VOLUMES

class SoundManager:
    """Manages game audio including sound effects and music."""
    
    # Sound parameters (frequency, duration, volume)
    SOUND_PARAMS = {
        'thrust': (220, 0.1, 0.3),      # Shorter, low rumble
        'shoot': (440, 0.05, 0.3),      # Quick medium pitch
        'explosion_large': (110, 0.4, 0.5),   # Long low boom
        'explosion_medium': (165, 0.3, 0.4),  # Medium boom
        'explosion_small': (220, 0.2, 0.3),   # Short higher boom
        'game_over': (165, 0.8, 0.4),   # Long low tone
        'level_complete': (440, 0.4, 0.4)  # Victory sound
    }
    
    def __init__(self):
        """Initialize the sound manager."""
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.volumes = AUDIO_VOLUMES.copy()
        
        # Ensure sounds directory exists
        self.sound_dir = os.path.join('assets', 'sounds')
        os.makedirs(self.sound_dir, exist_ok=True)
        
        # Load or generate sound effects
        for name in self.SOUND_PARAMS:
            self._ensure_sound_exists(name)
            self._load_sound(name)
        
        # Set volumes
        self.set_volume('sfx', self.volumes['sfx'])
        print("Sound manager initialized")  # Debug info
    
    def _generate_sine_wave(self, frequency: float, duration: float, volume: float = 0.5) -> bytes:
        """Generate a sine wave with given frequency and duration."""
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        samples = []
        
        # Add fade in/out to reduce popping
        fade_samples = int(0.005 * sample_rate)  # 5ms fade
        
        for i in range(num_samples):
            # Apply fade in/out
            fade_multiplier = 1.0
            if i < fade_samples:
                fade_multiplier = i / fade_samples
            elif i > num_samples - fade_samples:
                fade_multiplier = (num_samples - i) / fade_samples
            
            sample = volume * fade_multiplier * math.sin(2 * math.pi * frequency * i / sample_rate)
            samples.append(struct.pack('h', int(sample * 32767)))
        
        return b''.join(samples)
    
    def _create_sound_file(self, filename: str, frequency: float, duration: float, volume: float = 0.5) -> None:
        """Create a WAV file with given parameters."""
        try:
            with wave.open(filename, 'w') as wav_file:
                # Set parameters
                nchannels = 1
                sampwidth = 2
                framerate = 44100
                nframes = int(duration * framerate)
                comptype = 'NONE'
                compname = 'not compressed'
                
                # Set WAV file parameters
                wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
                
                # Write audio data
                wav_file.writeframes(self._generate_sine_wave(frequency, duration, volume))
            print(f"Created sound file: {filename}")  # Debug info
        except Exception as e:
            print(f"Error creating sound file {filename}: {e}")  # Debug info
    
    def _ensure_sound_exists(self, name: str) -> None:
        """Check if sound file exists, generate if it doesn't."""
        filename = os.path.join(self.sound_dir, f'{name}.wav')
        if not os.path.exists(filename):
            print(f"Generating missing sound file: {name}")  # Debug info
            freq, duration, volume = self.SOUND_PARAMS[name]
            self._create_sound_file(filename, freq, duration, volume)
    
    def _load_sound(self, name: str) -> None:
        """Load a sound effect."""
        try:
            filename = os.path.join(self.sound_dir, f'{name}.wav')
            if os.path.exists(filename):
                self.sounds[name] = pygame.mixer.Sound(filename)
                print(f"Loaded sound: {name}")  # Debug info
            else:
                print(f"Sound file not found: {filename}")  # Debug info
        except Exception as e:
            print(f"Error loading sound {name}: {e}")  # Debug info
    
    def play_sound(self, name: str) -> None:
        """Play a sound effect.
        
        Args:
            name: Name of the sound to play
        """
        if name in self.sounds:
            try:
                # Stop any currently playing instance of this sound
                self.sounds[name].stop()
                # Play the sound
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