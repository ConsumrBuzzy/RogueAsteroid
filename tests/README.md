# Test Suite Organization

## Directory Structure

```
tests/
├── conftest.py              # Shared test fixtures and configuration
├── pytest.ini              # Test configuration
├── run_tests.py            # Test runner script
│
├── unit/                   # Unit tests for individual components
│   ├── test_components.py  # Basic component tests
│   ├── test_entities.py    # Entity creation and basic behavior
│   └── test_utils.py       # Utility function tests
│
├── engine/                 # Game engine tests
│   ├── test_ecs.py        # Entity Component System
│   ├── test_physics.py    # Physics engine
│   └── test_graphics.py   # Graphics and rendering
│
├── game/                   # Game-specific tests
│   ├── test_game_state.py # Game state management
│   ├── test_scoring.py    # Scoring system
│   ├── test_collision.py  # Collision detection
│   └── test_systems.py    # Game systems
│
├── ui/                     # User interface tests
│   ├── test_menu.py       # Menu system
│   └── test_hud.py        # HUD elements
│
└── integration/           # Integration tests
    ├── test_gameplay.py   # End-to-end gameplay
    └── test_performance.py # Performance benchmarks
```

## Test Categories

1. **Unit Tests** (`@pytest.mark.unit`)
   - Individual component testing
   - Basic entity behavior
   - Utility functions

2. **Engine Tests** (`@pytest.mark.engine`)
   - ECS functionality
   - Physics calculations
   - Graphics rendering

3. **Game Tests** (`@pytest.mark.game`)
   - Game state management
   - Scoring system
   - Collision detection
   - Game systems

4. **UI Tests** (`@pytest.mark.ui`)
   - Menu functionality
   - HUD elements
   - User input

5. **Integration Tests** (`@pytest.mark.integration`)
   - System interactions
   - End-to-end gameplay
   - Performance benchmarks

## Running Tests

- Run all tests: `python -m pytest`
- Run specific category: `python -m pytest -m unit`
- Run specific directory: `python -m pytest tests/unit/`
- Run with coverage: `python -m pytest --cov=src`

## Adding New Tests

1. Place test file in appropriate directory
2. Use relevant pytest marks
3. Follow naming convention: `test_*.py`
4. Include docstrings explaining test purpose
5. Use fixtures from conftest.py where appropriate 