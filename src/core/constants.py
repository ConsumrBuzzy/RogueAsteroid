"""Game-wide constants."""

# Display settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TARGET_FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game settings
STARTING_LIVES = 3
INVULNERABILITY_TIME = 3.0  # Seconds of invulnerability after death

# Level settings
INITIAL_ASTEROIDS = 4     # Number of asteroids in first level
ASTEROIDS_INCREMENT = 2   # Additional asteroids per level
MAX_ASTEROIDS = 12       # Maximum asteroids in any level

# Physics settings
SHIP_ACCELERATION = 200.0  # Pixels/second^2
SHIP_MAX_SPEED = 300.0    # Pixels/second
SHIP_ROTATION_SPEED = 3.0  # Radians/second
SHIP_FRICTION = 0.99      # Velocity multiplier per second

# Weapon settings
BULLET_SPEED = 400.0      # Pixels/second
BULLET_LIFETIME = 1.0     # Seconds before despawning
MAX_BULLETS = 5           # Maximum bullets on screen

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

THRUST_PARTICLES = {
    'count': 5,
    'speed_range': (100, 200),
    'size_range': (1, 2),
    'lifetime_range': (0.1, 0.3),
    'spread_angle': 30.0  # Degrees
}

# Asteroid settings
ASTEROID_SPEED_MIN = 50.0  # Minimum asteroid speed
ASTEROID_SPEED_MAX = 150.0 # Maximum asteroid speed
ASTEROID_SPIN_MIN = 0.5    # Minimum rotation speed
ASTEROID_SPIN_MAX = 2.0    # Maximum rotation speed

# Scoring
ASTEROID_SCORE_LARGE = 20
ASTEROID_SCORE_MEDIUM = 50
ASTEROID_SCORE_SMALL = 100
EXTRA_LIFE_SCORE = 10000

# Debug settings
DEBUG_DRAW_COLLIDERS = False
DEBUG_SHOW_FPS = True 

# High score settings
MAX_HIGH_SCORES = 5  # Reduced from 10 to match current implementation
HIGH_SCORE_NAME_LENGTH = 10 