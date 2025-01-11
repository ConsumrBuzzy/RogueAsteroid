# RogueAsteroid

A classic arcade-style space shooter built with Python and Pygame, featuring physics-based movement, particle effects, and progressive difficulty.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Pygame 2.5.x
- NumPy 1.24.x

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/RogueAsteroid.git
cd RogueAsteroid

# Install dependencies
pip install -r requirements.txt

# Run the game
python src/main.py
```

## Gameplay

### Controls
- **Movement**:
  - Thrust: Up Arrow / W
  - Rotate Left: Left Arrow / A
  - Rotate Right: Right Arrow / D
  - Reverse Thrust: Down Arrow / S
- **Actions**:
  - Shoot: Space
  - Pause: P or Esc
  - Options: O
  - Return to Menu: M (when paused)

### Game Mechanics
- Pilot your ship through waves of asteroids
- Shoot asteroids to break them into smaller pieces
- Large asteroids split into medium, medium into small
- Points awarded based on asteroid size:
  - Small: 100 points
  - Medium: 75 points
  - Large: 50 points
- Extra life awarded every two levels (max 5 lives)
- Top 5 high scores are saved between sessions

### Tips
- Use thrust carefully - momentum carries in space!
- Watch your bullet count (max 12 on screen)
- Bullets have a short lifetime (0.5 seconds)
- Use screen wrapping to your advantage
- Clear asteroids methodically to avoid overwhelming situations

## Modding Guide

### Adding New Features

#### 1. Entity Components
New components can be added in `src/core/entities/components.py`:
```python
class NewComponent(Component):
    def __init__(self, entity):
        super().__init__(entity)
        # Add your initialization here

    def update(self):
        # Add your update logic here
```

#### 2. Particle Effects
Modify `src/core/particles.py` to add new effects:
```python
def create_new_effect(self, position, color=(255, 255, 255)):
    # Define particle parameters
    num_particles = random.randint(5, 10)
    # Create and configure particles
```

#### 3. Game Constants
Adjust game balance in `src/core/constants.py`:
```python
# Ship properties
SHIP_ACCELERATION = 250  # Pixels/second²
SHIP_MAX_SPEED = 400    # Pixels/second
SHIP_ROTATION_SPEED = 180  # Degrees/second

# Asteroid properties
ASTEROID_SPEED_RANGE = (50, 100)  # Pixels/second
```

### Common Modifications

1. **Adjusting Difficulty**:
   - Modify asteroid speeds in `constants.py`
   - Adjust wave progression in `game.py`
   - Change bullet lifetime or count

2. **Visual Changes**:
   - Update entity shapes in their respective classes
   - Modify particle effects parameters
   - Adjust color schemes

3. **Game Mechanics**:
   - Add power-ups by creating new entity types
   - Modify collision handling in `game.py`
   - Add new game states in `game_state.py`

### Project Structure
```
src/
├── core/          # Core game systems
├── entities/      # Game entities
└── ui/           # User interface
docs/
├── DEVELOPMENT_LOG.md      # Development history
├── GAME_DESIGN_DOCUMENT.md # Game specifications
└── TECHNICAL_DESIGN.md     # Technical details
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See `docs/PROJECT_CHARTER.md` for development guidelines.

## License
[MIT License](LICENSE)

## Acknowledgments
- Original Asteroids game by Atari
- Pygame community
- All contributors

---
Note: For detailed technical information, see the docs/ directory. 