"""Particle effect template configurations."""

# Standard effect templates
EFFECT_TEMPLATES = {
    'thrust': {
        'count': 10,
        'speed_range': (50, 100),
        'angle_spread': 30,
        'lifetime_range': (0.2, 0.4),
        'size_range': (1, 2),
        'colors': [(255, 200, 50), (255, 100, 0), (200, 50, 0)]
    },
    'explosion': {
        'count': 20,
        'speed_range': (100, 200),
        'angle_spread': 360,
        'lifetime_range': (0.5, 1.0),
        'size_range': (1, 3),
        'colors': [(255, 200, 50), (255, 100, 0), (200, 50, 0)]
    },
    'sparkle': {
        'count': 5,
        'speed_range': (20, 50),
        'angle_spread': 360,
        'lifetime_range': (0.3, 0.6),
        'size_range': (1, 1),
        'colors': [(255, 255, 200), (255, 255, 150), (255, 255, 100)]
    },
    'impact': {
        'count': 8,
        'speed_range': (80, 150),
        'angle_spread': 120,
        'lifetime_range': (0.2, 0.5),
        'size_range': (1, 2),
        'colors': [(255, 255, 255), (200, 200, 255)]
    },
    'debris': {
        'count': 15,
        'speed_range': (50, 150),
        'angle_spread': 360,
        'lifetime_range': (0.4, 0.8),
        'size_range': (1, 3),
        'colors': [(150, 150, 150), (100, 100, 100)]
    }
}

# Template validation schema
TEMPLATE_SCHEMA = {
    'count': int,
    'speed_range': tuple,
    'angle_spread': (int, float),
    'lifetime_range': tuple,
    'size_range': tuple,
    'colors': list
}

def validate_template(name: str, template: dict) -> bool:
    """Validate a particle effect template against the schema.
    
    Args:
        name: Template name
        template: Template configuration dictionary
        
    Returns:
        bool: True if template is valid
        
    Raises:
        ValueError: If template is invalid
    """
    # Check required fields
    missing_fields = [field for field in TEMPLATE_SCHEMA if field not in template]
    if missing_fields:
        raise ValueError(f"Template '{name}' missing required fields: {missing_fields}")
        
    # Validate field types
    for field, expected_type in TEMPLATE_SCHEMA.items():
        value = template[field]
        if not isinstance(value, expected_type):
            raise ValueError(
                f"Template '{name}' field '{field}' has invalid type. "
                f"Expected {expected_type}, got {type(value)}"
            )
            
    # Validate ranges
    for field in ['speed_range', 'lifetime_range', 'size_range']:
        value = template[field]
        if len(value) != 2 or value[0] > value[1]:
            raise ValueError(
                f"Template '{name}' has invalid {field}. "
                f"Must be (min, max) tuple with min <= max"
            )
            
    # Validate colors
    if not template['colors']:
        raise ValueError(f"Template '{name}' must have at least one color")
    
    for color in template['colors']:
        if not isinstance(color, tuple) or len(color) != 3:
            raise ValueError(
                f"Template '{name}' has invalid color {color}. "
                f"Must be RGB tuple (r,g,b)"
            )
            
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
            raise ValueError(
                f"Template '{name}' has invalid color values in {color}. "
                f"Must be integers 0-255"
            )
            
    return True 