"""Sound system for managing game audio."""
import os
import wave
import math
import struct
import pygame
from typing import Dict, Optional, Tuple

class SoundManager:
    """Manages game audio including sound effects and music."""
    
    SOUND_PARAMS = {
        'thrust': {'freq': 220, 'duration': 0.1, 'volume': 0.4},
        'shoot': {'freq': 440, 'duration': 0.05, 'volume': 0.3},
        'explosion_large': {'freq': 110, 'duration': 0.4, 'volume': 0.7},
        'explosion_medium': {'freq': 165, 'duration': 0.3, 'volume': 0.6},
        'explosion_small': {'freq': 220, 'duration': 0.2, 'volume': 0.5},
        'game_over': {'freq': 165, 'duration': 0.8, 'volume': 0.7},
        'level_complete': {'freq': 440, 'duration': 0.4, 'volume': 0.7}
    }
    
    def __init__(self):
        """Initialize the sound manager."""
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.sfx_volume = 0.7
        
        # Ensure sounds directory exists
        self.sounds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'sounds')
        os.makedirs(self.sounds_dir, exist_ok=True)
        
        # Load or generate sound effects
        for sound_name in self.SOUND_PARAMS:
            self._ensure_sound_exists(sound_name)
            self._load_sound(sound_name)
    
    def _generate_sine_wave(self, freq: float, duration: float, volume: float = 0.5) -> bytes:
        """Generate a sine wave with fade in/out."""
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        fade_samples = int(0.02 * sample_rate)  # 20ms fade
        
        samples = []
        for i in range(num_samples):
            # Calculate fade multiplier
            if i < fade_samples:
                fade = i / fade_samples
            elif i > num_samples - fade_samples:
                fade = (num_samples - i) / fade_samples
            else:
                fade = 1.0
                
            # Generate sample
            t = float(i) / sample_rate
            sample = int(32767.0 * volume * fade * math.sin(2.0 * math.pi * freq * t))
            samples.append(struct.pack('h', sample))
        
        return b''.join(samples)
    
    def _create_sound_file(self, sound_name: str) -> None:
        """Create a WAV file for a sound effect."""
        params = self.SOUND_PARAMS[sound_name]
        wav_data = self._generate_sine_wave(
            params['freq'],
            params['duration'],
            params['volume']
        )
        
        wav_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
        with wave.open(wav_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(44100)
            wav_file.writeframes(wav_data)
    
    def _ensure_sound_exists(self, sound_name: str) -> None:
        """Check if sound file exists, generate if it doesn't."""
        wav_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
        if not os.path.exists(wav_path):
            print(f"Generating sound file: {sound_name}.wav")
            self._create_sound_file(sound_name)
    
    def _load_sound(self, sound_name: str) -> None:
        """Load a sound effect from file."""
        wav_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
        try:
            sound = pygame.mixer.Sound(wav_path)
            sound.set_volume(self.sfx_volume * self.SOUND_PARAMS[sound_name]['volume'])
            self.sounds[sound_name] = sound
            print(f"Loaded sound: {sound_name}")
        except pygame.error as e:
            print(f"Warning: Could not load sound '{sound_name}': {e}")
            self.sounds[sound_name] = None
    
    def play_sound(self, name: str) -> None:
        """Play a sound effect."""
        if name in self.sounds and self.sounds[name] is not None:
            # Stop the sound if it's already playing to prevent overlapping
            self.sounds[name].stop()
            self.sounds[name].play()
    
    def set_volume(self, volume: float) -> None:
        """Set the volume for all sound effects."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for name, sound in self.sounds.items():
            if sound is not None:
                sound.set_volume(self.sfx_volume * self.SOUND_PARAMS[name]['volume']) 