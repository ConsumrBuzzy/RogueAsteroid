"""Asteroid settings constants."""

MAX_ASTEROIDS = 12

ASTEROID_SIZES = {
    'large': {
        'radius': 40,
        'speed_range': (50, 100),
        'mass': 9.0,
        'points': 3,
        'vertices_range': (10, 14)  # More vertices for larger asteroids
    },
    'medium': {
        'radius': 20,
        'speed_range': (100, 150),
        'mass': 4.0,
        'points': 2,
        'vertices_range': (8, 12)  # Medium complexity
    },
    'small': {
        'radius': 10,
        'speed_range': (150, 200),
        'mass': 1.0,
        'points': 1,
        'vertices_range': (6, 10)  # Simpler shape for small asteroids
    }
} 