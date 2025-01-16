"""
Audio management for the ECS game.
"""

import os
import pygame
from typing import Dict, Optional
from dataclasses import dataclass
from .resources import Resources, GameSettings

@dataclass
class AudioResource:
    """Resource for storing game audio."""
    sounds: Dict[str, pygame.mixer.Sound]
    music: Dict[str, str]  # Music files are loaded on demand

def load_sound(name: str) -> Optional[pygame.mixer.Sound]:
    """Load a sound effect from the assets directory."""
    try:
        fullpath = os.path.join("assets", "sounds", f"{name}.wav")
        return pygame.mixer.Sound(fullpath)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading sound {name}: {e}")
        return None

def init_audio(resources: Resources) -> None:
    """Initialize game audio."""
    pygame.mixer.init()
    
    sounds = {}
    music = {}
    
    # Load sound effects
    sound_files = [
        "shoot",
        "explosion_large",
        "explosion_medium",
        "explosion_small",
        "thrust",
        "game_over",
        "level_up"
    ]
    
    for sound_name in sound_files:
        if sound := load_sound(sound_name):
            sounds[sound_name] = sound
    
    # Register music files
    music_files = [
        "menu",
        "game",
        "game_over"
    ]
    
    for music_name in music_files:
        music_path = os.path.join("assets", "music", f"{music_name}.ogg")
        if os.path.exists(music_path):
            music[music_name] = music_path
    
    # Store audio in resources
    resources.add(AudioResource(sounds=sounds, music=music))

def play_sound(resources: Resources, name: str) -> None:
    """Play a sound effect."""
    settings = resources.get(GameSettings)
    audio = resources.get(AudioResource)
    
    if not settings or not settings.sound_enabled or not audio:
        return
        
    if sound := audio.sounds.get(name):
        sound.set_volume(settings.sfx_volume)
        sound.play()

def play_music(resources: Resources, name: str, loop: bool = True) -> None:
    """Play background music."""
    settings = resources.get(GameSettings)
    audio = resources.get(AudioResource)
    
    if not settings or not settings.sound_enabled or not audio:
        return
        
    if music_path := audio.music.get(name):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(settings.music_volume)
        pygame.mixer.music.play(-1 if loop else 0)

def stop_music() -> None:
    """Stop currently playing music."""
    pygame.mixer.music.stop()

def pause_music() -> None:
    """Pause currently playing music."""
    pygame.mixer.music.pause()

def unpause_music() -> None:
    """Unpause currently playing music."""
    pygame.mixer.music.unpause()
