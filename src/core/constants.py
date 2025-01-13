"""Game constants."""

# Display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Explosion colors
EXPLOSION_COLORS = [
    (255, 69, 0),    # Red-orange
    (255, 140, 0),   # Dark orange
    (255, 165, 0),   # Orange
    (255, 215, 0),   # Yellow
]

# Thrust colors
THRUST_COLORS = [
    (200, 200, 200),  # Light gray
    (180, 180, 180),  # Medium gray
    (160, 160, 160),  # Dark gray
]

# Ship
SHIP_ACCELERATION = 300.0
SHIP_MAX_SPEED = 300.0
SHIP_ROTATION_SPEED = 180.0  # Degrees per second
SHIP_FRICTION = 0.02
SHIP_INVULNERABLE_TIME = 3.0

# Bullets
BULLET_SPEED = 500.0
BULLET_LIFETIME = 1.0
MAX_BULLETS = 4

# Asteroids
MAX_ASTEROIDS = 12
ASTEROID_SIZES = {
    'large': {
        'radius': 40,
        'speed_range': (50, 100),
        'mass': 9.0,
        'points': 3
    },
    'medium': {
        'radius': 20,
        'speed_range': (100, 150),
        'mass': 4.0,
        'points': 2
    },
    'small': {
        'radius': 10,
        'speed_range': (150, 200),
        'mass': 1.0,
        'points': 1
    }
} 