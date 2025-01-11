"""Game constants and configuration."""

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game settings
INITIAL_LIVES = 3

# Ship settings
SHIP_ACCELERATION = 200.0  # Pixels per second squared
SHIP_MAX_SPEED = 300.0    # Pixels per second
SHIP_ROTATION_SPEED = 3.0  # Degrees per frame
SHIP_FRICTION = 0.02      # Velocity multiplier per frame
SHIP_INVULNERABLE_TIME = 2.0  # Seconds of invulnerability after spawn

# Bullet settings
BULLET_SPEED = 500.0      # Pixels per second
BULLET_LIFETIME = 1.0     # Seconds
BULLET_COOLDOWN = 0.25    # Seconds between shots

# Asteroid settings
ASTEROID_SIZES = {
    'large': {
        'radius': 40.0,
        'points': 20,
        'splits': 2,
        'speed_range': (50.0, 100.0),
        'vertices_range': (10, 14),
        'mass': 3.0
    },
    'medium': {
        'radius': 20.0,
        'points': 50,
        'splits': 2,
        'speed_range': (75.0, 150.0),
        'vertices_range': (8, 12),
        'mass': 2.0
    },
    'small': {
        'radius': 10.0,
        'points': 100,
        'splits': 0,
        'speed_range': (100.0, 200.0),
        'vertices_range': (6, 10),
        'mass': 1.0
    }
}

# Level settings
INITIAL_ASTEROIDS = 4     # Number of asteroids in first level
ASTEROIDS_INCREMENT = 2   # Additional asteroids per level
MAX_ASTEROIDS = 12       # Maximum asteroids in any level

# Particle effects
EXPLOSION_PARTICLES = {
    'large': {
        'count': 30,
        'speed_range': (100, 200),
        'size_range': (2, 4),
        'lifetime_range': (0.5, 1.0)
    },
    'medium': {
        'count': 20,
        'speed_range': (75, 150),
        'size_range': (1.5, 3),
        'lifetime_range': (0.3, 0.8)
    },
    'small': {
        'count': 15,
        'speed_range': (50, 100),
        'size_range': (1, 2),
        'lifetime_range': (0.2, 0.5)
    }
}

THRUST_PARTICLES = {
    'count': 5,
    'speed_range': (100, 200),
    'size_range': (1, 2),
    'lifetime_range': (0.1, 0.3),
    'spread_angle': 30.0  # Degrees
}

# Audio settings
AUDIO_VOLUMES = {
    'music': 0.5,
    'sfx': 0.7
}

# High score settings
MAX_HIGH_SCORES = 10
HIGH_SCORE_NAME_LENGTH = 10 