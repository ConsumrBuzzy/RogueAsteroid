# Project Structure

## Directory Layout

```
RogueAsteroid/
├── docs/
│   ├── api/              # API documentation
│   ├── design/           # Design documents
│   ├── logs/            
│   │   ├── runtime/      # Runtime logs
│   │   └── debug/        # Debug logs
│   ├── DEVELOPMENT_LOG.md
│   ├── GAME_DESIGN.md
│   └── PROJECT_CHARTER.md
│
├── src/
│   ├── core/
│   │   ├── components/   # Individual component implementations
│   │   ├── config/       # Configuration and settings
│   │   ├── entities/     # Entity system and base classes
│   │   ├── events/       # Event system
│   │   ├── resources/    # Resource management
│   │   ├── services/     # Game services
│   │   ├── state/        # Game state management
│   │   ├── constants.py  # Game constants
│   │   ├── game.py       # Main game loop
│   │   └── logging.py    # Logging configuration
│   │
│   └── __init__.py
│
├── tests/
│   ├── test_components.py
│   ├── test_additional_components.py
│   ├── test_entities.py
│   ├── test_effects.py
│   ├── test_performance.py
│   ├── test_ship.py
│   ├── test_system.py
│   ├── test_utils.py
│   ├── test_integration.py
│   ├── conftest.py
│   ├── pytest.ini
│   └── run_tests.py
│
├── README.md
└── requirements.txt
```

## Key Components

### Core Components
- `TransformComponent`: Position, rotation, and movement
- `RenderComponent`: Visual representation
- `CollisionComponent`: Collision detection
- `PhysicsComponent`: Physics simulation
- `InputComponent`: Input handling
- `EffectComponent`: Visual effects
- `ScreenWrapComponent`: Screen boundary handling

### Entity System
- `Entity`: Base class for game objects
- `Component`: Base class for all components
- Component registry for type management

### Testing Structure
- Unit tests for individual components
- Integration tests for component interactions
- Performance tests for optimization
- System tests for game mechanics
- Utility tests for helper functions

## File Descriptions

### Documentation
- `DEVELOPMENT_LOG.md`: Progress tracking and task management
- `GAME_DESIGN.md`: Game mechanics and features
- `PROJECT_CHARTER.md`: Project goals and methodology

### Source Code
- `constants.py`: Game-wide constants and configuration
- `game.py`: Main game loop and initialization
- `logging.py`: Logging system configuration

### Testing
- `run_tests.py`: Test runner with coverage support
- `conftest.py`: Test fixtures and configuration
- `pytest.ini`: PyTest configuration

## Development Guidelines

1. Follow PEP 8 style guide
2. Document all classes and methods
3. Write tests for new features
4. Update DEVELOPMENT_LOG.md for changes
5. Maintain clean component separation
6. Use type hints and docstrings 