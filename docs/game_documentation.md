# RogueAsteroid Game Documentation

## Overview
RogueAsteroid is a classic arcade-style space shooter implemented in Python using the Pygame library. The game features physics-based movement, particle effects, and progressive difficulty scaling.

## Project Structure

```
RogueAsteroid/
├── assets/          # Game assets (images, sounds)
├── data/            # Game data files
├── docs/            # Documentation
├── src/             # Source code
│   ├── core/        # Core game systems
│   ├── entities/    # Game entities (ship, asteroids)
│   └── main.py      # Main entry point
├── tests/           # Unit tests
└── requirements.txt # Project dependencies
```

## Core Systems

### Game Engine (`src/core/game.py`)
- Main game loop management
- State management (menu, gameplay, pause)
- Physics and collision detection
- Level progression
- Score tracking

### Game States
- Menu
- Active Gameplay
- Paused
- Game Over

### Scoring System
- Small Asteroid: 100 points
- Medium Asteroid: 75 points
- Large Asteroid: 50 points
- Extra life awarded every two levels (max 5 lives)

## Controls

### Default Control Scheme
| Action         | Key           |
|---------------|---------------|
| Thrust        | Up Arrow / W  |
| Rotate Left   | Left Arrow / A|
| Rotate Right  | Right Arrow / D|
| Reverse       | Down Arrow / S|
| Shoot         | Space         |
| Pause         | P or Esc      |
| Options       | O             |
| Menu Return   | M (when paused)|

## Game Mechanics

### Ship Physics
- Realistic momentum-based movement
- Thrust affects velocity
- Inertia continues movement in space
- Wrapping around screen edges

### Asteroid Behavior
- Asteroids split into smaller pieces when shot
- Three size categories: Large, Medium, Small
- Random movement patterns
- Screen wrapping

### Level Progression
- Increasing number of asteroids
- Progressive difficulty scaling
- Higher asteroid speeds in later levels

## Technical Details

### Dependencies
- Python 3.8+
- Pygame 2.5.x
- NumPy 1.24.x

### Installation
```bash
pip install -r requirements.txt
```

### Running the Game
```bash
python src/main.py
```

### Development Setup
```bash
pip install -r requirements-dev.txt  # Includes testing dependencies
```

## Testing
- Unit tests available in `/tests` directory
- Run tests using pytest:
```bash
pytest
```

## Performance Considerations
- Particle effects optimized for performance
- Collision detection uses spatial partitioning
- Frame rate capped for consistent experience

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## License
This project is licensed under the terms included in the LICENSE file.
