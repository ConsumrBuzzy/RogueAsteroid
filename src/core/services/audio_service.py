"""Service for managing game audio."""
from typing import Dict, Optional
import pygame

class AudioService:
    """Service for managing game audio.
    
    Provides:
    - Sound effect playback
    - Music playback
    - Volume control
    - Audio state management
    - Debug support
    """
    
    def __init__(self):
        """Initialize the audio service."""
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._current_music: Optional[str] = None
        self._sound_volume = 1.0
        self._music_volume = 0.5
        self._enabled = True
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            print("AudioService initialized")
        except Exception as e:
            print(f"Warning: Failed to initialize audio: {e}")
            self._enabled = False
    
    def load_sound(self, name: str, sound: pygame.mixer.Sound) -> None:
        """Load a sound effect.
        
        Args:
            name: Name to store sound under
            sound: Sound to store
        """
        self._sounds[name] = sound
        sound.set_volume(self._sound_volume)
        print(f"Loaded sound: {name}")
    
    def play_sound(self, name: str) -> None:
        """Play a sound effect.
        
        Args:
            name: Name of sound to play
        """
        if not self._enabled:
            return
            
        if name in self._sounds:
            self._sounds[name].play()
            print(f"Playing sound: {name}")
        else:
            print(f"Warning: Sound not found: {name}")
    
    def play_music(self, path: str, loops: int = -1) -> None:
        """Play background music.
        
        Args:
            path: Path to music file
            loops: Number of times to loop (-1 for infinite)
        """
        if not self._enabled:
            return
            
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(loops)
            self._current_music = path
            print(f"Playing music: {path}")
        except Exception as e:
            print(f"Error playing music: {e}")
    
    def stop_music(self) -> None:
        """Stop currently playing music."""
        if not self._enabled:
            return
            
        pygame.mixer.music.stop()
        self._current_music = None
        print("Stopped music")
    
    def pause_music(self) -> None:
        """Pause currently playing music."""
        if not self._enabled:
            return
            
        pygame.mixer.music.pause()
        print("Paused music")
    
    def resume_music(self) -> None:
        """Resume paused music."""
        if not self._enabled:
            return
            
        pygame.mixer.music.unpause()
        print("Resumed music")
    
    def set_sound_volume(self, volume: float) -> None:
        """Set sound effect volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self._sound_volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            sound.set_volume(self._sound_volume)
        print(f"Set sound volume: {self._sound_volume}")
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self._music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._music_volume)
        print(f"Set music volume: {self._music_volume}")
    
    def enable(self) -> None:
        """Enable audio playback."""
        self._enabled = True
        if self._current_music:
            self.resume_music()
        print("Audio enabled")
    
    def disable(self) -> None:
        """Disable audio playback."""
        self._enabled = False
        if self._current_music:
            self.pause_music()
        print("Audio disabled")
    
    def is_enabled(self) -> bool:
        """Check if audio is enabled.
        
        Returns:
            True if audio is enabled
        """
        return self._enabled
    
    def cleanup(self) -> None:
        """Clean up the service."""
        if self._enabled:
            self.stop_music()
            pygame.mixer.quit()
        self._sounds.clear()
        print("AudioService cleaned up") 