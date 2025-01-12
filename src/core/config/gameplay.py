"""Gameplay configuration."""

# Game settings
STARTING_LIVES = 3
INITIAL_ASTEROIDS = 4
ASTEROIDS_PER_LEVEL = 2
EXTRA_LIFE_SCORE = 10000

# Physics settings
FRICTION = 0.99
MAX_SPEED = 400.0
ROTATION_SPEED = 180.0
THRUST_FORCE = 300.0
PHYSICS_TIME_STEP = 1.0 / 60.0
PHYSICS_VELOCITY_ITERATIONS = 8
PHYSICS_POSITION_ITERATIONS = 3

# Collision settings
COLLISION_MARGIN = 2  # pixels

# Level settings
INITIAL_ASTEROIDS = 4
ASTEROIDS_INCREMENT = 2
MAX_ASTEROIDS = 12

# Game states
MENU_STATE = "menu"
GAME_STATE = "game"
PAUSE_STATE = "pause"
GAME_OVER_STATE = "game_over"
HIGH_SCORE_STATE = "high_score"

# Statistics tracking
STAT_ASTEROIDS_DESTROYED = "asteroids_destroyed"
STAT_BULLETS_FIRED = "bullets_fired"
STAT_DEATHS = "deaths"
STAT_TIME_PLAYED = "time_played"
STAT_HIGH_SCORE = "high_score"

# Achievements
ACHIEVEMENT_FIRST_KILL = "first_kill"
ACHIEVEMENT_SURVIVOR = "survivor"
ACHIEVEMENT_SHARPSHOOTER = "sharpshooter" 