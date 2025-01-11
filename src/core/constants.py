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
STARTING_LIVES = 3  # Number of lives player starts with
SHIP_INVULNERABLE_TIME = 2.0  # Seconds of invulnerability after respawn
MAX_ASTEROIDS = 10  # Maximum number of asteroids on screen
MAX_BULLETS = 8  # Maximum number of bullets on screen

# Ship settings
SHIP_ACCELERATION = 400  # Pixels per second squared
SHIP_MAX_SPEED = 400  # Maximum speed in pixels per second
SHIP_ROTATION_SPEED = 180  # Degrees per second
SHIP_FRICTION = 0.02  # Velocity reduction per frame (0-1)

# Bullet settings
BULLET_SPEED = 1200.0  # pixels per second
BULLET_LIFETIME = 0.5  # seconds before despawning

# Asteroid settings
ASTEROID_SIZES = {
    'large': {
        'radius': 40.0,
        'points': 3,
        'splits': 2,
        'speed_range': (50.0, 100.0),
        'vertices_range': (10, 14),
        'mass': 3.0
    },
    'medium': {
        'radius': 20.0,
        'points': 2,
        'splits': 2,
        'speed_range': (75.0, 150.0),
        'vertices_range': (8, 12),
        'mass': 2.0
    },
    'small': {
        'radius': 10.0,
        'points': 1,
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