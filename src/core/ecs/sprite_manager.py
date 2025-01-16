"""
Sprite and asset management for the ECS game.
"""

import os
import pygame
from typing import Dict, Optional
from dataclasses import dataclass
from .resources import Resources

@dataclass
class SpriteResource:
    """Resource for storing game sprites."""
    sprites: Dict[str, pygame.Surface]

def load_sprite(name: str, colorkey: Optional[tuple] = None) -> Optional[pygame.Surface]:
    """Load a sprite from the assets directory."""
    try:
        fullpath = os.path.join("assets", "sprites", f"{name}.png")
        image = pygame.image.load(fullpath)
        
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
            
        return image.convert_alpha()
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error loading sprite {name}: {e}")
        return None

def init_sprites(resources: Resources) -> None:
    """Initialize all game sprites."""
    sprites = {}
    
    # Load player ship
    ship = load_sprite("ship", (0, 0, 0))
    if ship:
        sprites["ship"] = ship
        # Add thrust version
        ship_thrust = load_sprite("ship_thrust", (0, 0, 0))
        if ship_thrust:
            sprites["ship_thrust"] = ship_thrust
    
    # Load asteroids
    for size in ["large", "medium", "small"]:
        for variant in range(1, 4):  # 3 variants of each size
            asteroid = load_sprite(f"asteroid_{size}_{variant}", (0, 0, 0))
            if asteroid:
                sprites[f"asteroid_{size}_{variant}"] = asteroid
    
    # Load bullet
    bullet = load_sprite("bullet", (0, 0, 0))
    if bullet:
        sprites["bullet"] = bullet
    
    # Load particle effects
    for effect in ["explosion", "thrust"]:
        particle = load_sprite(f"particle_{effect}", (0, 0, 0))
        if particle:
            sprites[f"particle_{effect}"] = particle
    
    # Store sprites in resources
    resources.add(SpriteResource(sprites=sprites))
