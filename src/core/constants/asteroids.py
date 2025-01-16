"""
Asteroid-related constants.
"""

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
    "medium": (100, 150),
    "small": (150, 200)
}
ASTEROID_SPLIT_COUNT = 2
MIN_ASTEROID_COUNT = 4