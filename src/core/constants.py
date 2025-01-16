"""
Game-wide constants.
"""

# Window settings
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 640
WINDOW_TITLE = "Rogue Asteroid"
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_ACCELERATION = 200.0
PLAYER_MAX_SPEED = 500.0
PLAYER_ROTATION_SPEED = 360.0  # Degrees per second
PLAYER_FRICTION = 0.1
PLAYER_INVULNERABLE_TIME = 3.0
PLAYER_SHOOT_COOLDOWN = 0.2
PLAYER_INITIAL_LIVES = 3

# Bullet settings
BULLET_SPEED = 800.0
BULLET_LIFETIME = 0.5
BULLET_DAMAGE = 1

# Asteroid settings
ASTEROID_SIZES = ["large", "medium", "small"]
ASTEROID_POINTS = {
    "large": 20,
    "medium": 50,
    "small": 100
}
ASTEROID_RADIUS = {
    "large": 40,
    "medium": 20,
    "small": 10
}
ASTEROID_SPEED = {
    "large": (50, 100),  # (min, max) speed
    "medium": (75, 150),
    "small": (100, 200)
}
ASTEROID_SPLIT_COUNT = 2
MIN_ASTEROID_COUNT = 4

# Particle effects
EXPLOSION_PARTICLE_COUNT = 20
EXPLOSION_PARTICLE_LIFETIME = 1.0
EXPLOSION_PARTICLE_SPEED = 200.0
THRUST_PARTICLE_COUNT = 5
THRUST_PARTICLE_LIFETIME = 0.5
THRUST_PARTICLE_SPEED = 100.0
PARTICLE_COLORS = [
    (255, 255, 255),  # White
    (255, 255, 0),    # Yellow
    (255, 165, 0),    # Orange
    (255, 0, 0)       # Red
]

# Menu settings
MENU_FONT_SIZE = 32
MENU_COLOR = WHITE
MENU_HOVER_COLOR = YELLOW
MENU_SPACING = 50

# Sound settings
SOUND_VOLUME = 0.7
MUSIC_VOLUME = 0.5

# Asset paths
ASSET_DIR = "assets"
SPRITE_DIR = f"{ASSET_DIR}/sprites"
SOUND_DIR = f"{ASSET_DIR}/sounds"
MUSIC_DIR = f"{ASSET_DIR}/music"
FONT_DIR = f"{ASSET_DIR}/fonts"

# Layer settings (higher numbers render on top)
LAYER_BACKGROUND = 0
LAYER_PARTICLES = 1
LAYER_ASTEROIDS = 2
LAYER_BULLETS = 3
LAYER_PLAYER = 4
LAYER_UI = 5