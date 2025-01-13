"""Constants package for the game."""

from .display import *
from .colors import *
from .particles import *
from .game_settings import *
from .ship import *
from .weapons import *
from .asteroids import *

__all__ = (
    # Display
    'WINDOW_WIDTH', 'WINDOW_HEIGHT', 'FPS',
    # Colors
    'WHITE', 'BLACK', 'RED', 'GREEN', 'BLUE',
    # Particles
    'EXPLOSION_COLORS', 'THRUST_COLORS',
    'PARTICLE_MIN_LIFETIME', 'PARTICLE_MAX_LIFETIME',
    'THRUST_PARTICLE_COUNT', 'THRUST_PARTICLE_SPEED',
    'THRUST_PARTICLE_SPREAD', 'THRUST_PARTICLE_SIZE',
    # Game Settings
    'STARTING_LIVES', 'SCORE_MULTIPLIER', 'HIGH_SCORE_COUNT',
    # Ship
    'SHIP_ACCELERATION', 'SHIP_MAX_SPEED', 'SHIP_ROTATION_SPEED',
    'SHIP_FRICTION', 'SHIP_INVULNERABLE_TIME',
    # Weapons
    'BULLET_SPEED', 'BULLET_LIFETIME', 'MAX_BULLETS',
    # Asteroids
    'MAX_ASTEROIDS', 'ASTEROID_SIZES'
) 