"""Sound system for managing game audio."""
import os
import wave
import math
import struct
import random
import pygame
from typing import Dict, Optional

class SoundManager:
    """Manages game audio including sound effects and music."""
    
    SOUND_PARAMS = {
        'test': {  # Simple test sound
            'freq': 440,  # A4 note
            'duration': 0.5,
            'volume': 1.0,
            'fade': False
        },
        'thrust': {
            'freq': 110,  # Lower frequency for engine rumble
            'duration': 0.2,
            'volume': 0.4,
            'fade': True
        },
        'shoot': {
            'freq': 880,  # Higher pitch for laser
            'duration': 0.1,
            'volume': 0.3,
            'fade': True
        },
        'explosion_large': {
            'freq': 100,
            'duration': 0.4,
            'volume': 0.7,
            'noise': True
        },
        'explosion_medium': {
            'freq': 150,
            'duration': 0.3,
            'volume': 0.6,
            'noise': True
        },
        'explosion_small': {
            'freq': 200,
            'duration': 0.2,
            'volume': 0.5,
            'noise': True
        },
        'game_over': {
            'freq': 220,
            'duration': 0.8,
            'volume': 0.7,
            'fade': True
        },
        'level_complete': {
            'freq': 440,
            'duration': 0.4,
            'volume': 0.7,
            'fade': True
        }
    }
    
    def __init__(self):
        """Initialize the sound manager."""
        try:
            pygame.mixer.quit()  # Ensure mixer is stopped
            pygame.mixer.init(44100, -16, 1, 512)
            if not pygame.mixer.get_init():
                raise Exception("Mixer initialization failed")
            print("Mixer initialized successfully")  # Debug info
            
            self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
            self.sfx_volume = 0.7
            
            # Ensure sounds directory exists
            self.sounds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'sounds')
            os.makedirs(self.sounds_dir, exist_ok=True)
            print(f"Sound directory: {self.sounds_dir}")  # Debug info
            
            # Load or generate sound effects
            for sound_name in self.SOUND_PARAMS:
                print(f"\nProcessing sound: {sound_name}")  # Debug info
                self._ensure_sound_exists(sound_name)
                self._load_sound(sound_name)
        except Exception as e:
            print(f"Error initializing sound manager: {e}")
            raise
    
    def _generate_samples(self, sound_name: str) -> bytes:
        """Generate audio samples for a sound effect."""
        try:
            params = self.SOUND_PARAMS[sound_name]
            sample_rate = 44100
            num_samples = int(params['duration'] * sample_rate)
            print(f"Generating {num_samples} samples for {sound_name}")  # Debug info
            
            # Generate base waveform
            samples = []
            for i in range(num_samples):
                t = float(i) / sample_rate
                
                # Calculate amplitude envelope
                if params.get('fade', False):
                    fade_time = min(0.1, params['duration'] / 4)
                    if t < fade_time:
                        envelope = t / fade_time
                    elif t > params['duration'] - fade_time:
                        envelope = (params['duration'] - t) / fade_time
                    else:
                        envelope = 1.0
                else:
                    envelope = 1.0
                
                # Generate sample
                if params.get('noise', False):
                    # Noise-based sound (for explosions)
                    sample = random.uniform(-1, 1)
                    # Add some tone for character
                    sample = 0.7 * sample + 0.3 * math.sin(2.0 * math.pi * params['freq'] * t)
                else:
                    # Tonal sound
                    sample = math.sin(2.0 * math.pi * params['freq'] * t)
                
                # Apply envelope and volume
                sample = int(32767.0 * params['volume'] * envelope * sample)
                sample = max(-32767, min(32767, sample))
                samples.append(struct.pack('h', sample))
            
            result = b''.join(samples)
            print(f"Generated {len(result)} bytes of audio data")  # Debug info
            return result
        except Exception as e:
            print(f"Error generating samples for {sound_name}: {e}")
            raise
    
    def _create_sound_file(self, sound_name: str) -> None:
        """Create a WAV file for a sound effect."""
        try:
            wav_data = self._generate_samples(sound_name)
            wav_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
            print(f"Generated {len(wav_data)} bytes of audio data for {sound_name}")  # Debug info
            
            with wave.open(wav_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(44100)
                wav_file.writeframes(wav_data)
                print(f"Created sound file: {wav_path}")  # Debug info
            
            # Verify file was created and has content
            if os.path.exists(wav_path):
                size = os.path.getsize(wav_path)
                print(f"Verified sound file: {wav_path} (size: {size} bytes)")
            else:
                print(f"Error: Sound file not created: {wav_path}")
        except Exception as e:
            print(f"Error creating sound file {sound_name}: {e}")
            raise
    
    def _ensure_sound_exists(self, sound_name: str) -> None:
        """Check if sound file exists, generate if it doesn't."""
        wav_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
        if not os.path.exists(wav_path):
            print(f"Generating sound file: {sound_name}.wav")
            self._create_sound_file(sound_name)
        else:
            print(f"Sound file exists: {sound_name}.wav")  # Debug info
    
    def _load_sound(self, sound_name: str) -> None:
        """Load a sound effect from file."""
        wav_path = os.path.join(self.sounds_dir, f"{sound_name}.wav")
        try:
            sound = pygame.mixer.Sound(wav_path)
            sound.set_volume(self.sfx_volume * self.SOUND_PARAMS[sound_name]['volume'])
            self.sounds[sound_name] = sound
            print(f"Loaded sound: {sound_name}")  # Debug info
        except pygame.error as e:
            print(f"Warning: Could not load sound '{sound_name}': {e}")
            self.sounds[sound_name] = None
    
    def play_sound(self, name: str) -> None:
        """Play a sound effect."""
        if name in self.sounds and self.sounds[name] is not None:
            try:
                # Stop the sound if it's already playing to prevent overlapping
                self.sounds[name].stop()
                self.sounds[name].play()
                print(f"Playing sound: {name}")  # Debug info
            except pygame.error as e:
                print(f"Error playing sound '{name}': {e}")
    
    def set_volume(self, volume: float) -> None:
        """Set the volume for all sound effects."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for name, sound in self.sounds.items():
            if sound is not None:
                sound.set_volume(self.sfx_volume * self.SOUND_PARAMS[name]['volume']) 
    
    def play_test(self) -> None:
        """Play test sound to verify system is working."""
        print("Playing test sound...")  # Debug info
        self.play_sound('test') 