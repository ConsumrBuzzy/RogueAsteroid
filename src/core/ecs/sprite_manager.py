"""
Sprite and asset management for the ECS game.
"""

import os
import math
import pygame
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from .resources import Resources

@dataclass
class SpriteResource:
    """Resource for storing game sprites and default shapes."""
    sprites: Dict[str, pygame.Surface]
    shapes: Dict[str, List[Tuple[float, float]]]

def create_default_shapes() -> Dict[str, List[Tuple[float, float]]]:
    """Create default vector shapes for entities."""
    shapes = {}
    
    # Ship shape (triangle)
    shapes["ship"] = [(0, -20), (-10, 10), (10, 10)]
    
    # Bullet shape (small triangle)
    shapes["bullet"] = [(0, -4), (-2, 2), (2, 2)]
    
    # Asteroid shapes
    # Large asteroids
    shapes["asteroid_large_1"] = [
        (0, -40), (28, -28), (40, 0), 
        (28, 28), (0, 40), (-28, 28),
        (-40, 0), (-28, -28)
    ]
    
    shapes["asteroid_large_2"] = [
        (0, -35), (35, -15), (35, 15),
        (0, 35), (-35, 15), (-35, -15)
    ]
    
    shapes["asteroid_large_3"] = [
        (0, -40), (40, 0), (0, 40),
        (-40, 20), (-40, -20)
    ]
    
    # Medium asteroids
    shapes["asteroid_medium_1"] = [
        (0, -25), (18, -18), (25, 0),
        (18, 18), (0, 25), (-18, 18),
        (-25, 0), (-18, -18)
    ]
    
    shapes["asteroid_medium_2"] = [
        (0, -20), (20, -10), (20, 10),
        (0, 20), (-20, 10), (-20, -10)
    ]
    
    shapes["asteroid_medium_3"] = [
        (0, -25), (25, 0), (0, 25),
        (-25, 12), (-25, -12)
    ]
    
    # Small asteroids
    shapes["asteroid_small_1"] = [
        (0, -15), (10, -10), (15, 0),
        (10, 10), (0, 15), (-10, 10),
        (-15, 0), (-10, -10)
    ]
    
    shapes["asteroid_small_2"] = [
        (0, -12), (12, -6), (12, 6),
        (0, 12), (-12, 6), (-12, -6)
    ]
    
    shapes["asteroid_small_3"] = [
        (0, -15), (15, 0), (0, 15),
        (-15, 8), (-15, -8)
    ]
    
    # Particle shapes (single point)
    shapes["particle_explosion"] = [(0, 0)]
    shapes["particle_thrust"] = [(0, 0)]
    
    return shapes

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
    
    # Create default shapes for when sprites are not available
    shapes = create_default_shapes()
    
    # Store sprites and shapes in resources
    resources.add(SpriteResource(sprites=sprites, shapes=shapes))
