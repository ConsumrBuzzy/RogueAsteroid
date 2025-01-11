# RogueAsteroid Quick Start Guide

## For Players

### Getting Started
1. Install Python 3.8 or higher
2. Clone the repository and install dependencies (see README.md)
3. Run `python src/main.py`
4. Use arrow keys or WASD to control your ship
5. Press SPACE to shoot asteroids
6. Press P or ESC to pause

### Basic Controls
- **Movement**
  * THRUST: Up Arrow / W
  * ROTATE LEFT: Left Arrow / A
  * ROTATE RIGHT: Right Arrow / D
  * REVERSE: Down Arrow / S
- **Actions**
  * SHOOT: Space
  * PAUSE: P or Esc
  * OPTIONS: O
  * MENU: M (when paused)

### Gameplay Tips
1. **Movement**
   - Use short bursts of thrust for precise control
   - Remember you have momentum in space
   - Use reverse thrust to slow down
   - Screen wrapping can help escape tight situations

2. **Combat**
   - Large asteroids split into medium ones
   - Medium asteroids split into small ones
   - Small asteroids are destroyed completely
   - You can only have 12 bullets on screen
   - Bullets disappear after 0.5 seconds

3. **Scoring**
   - Small Asteroids: 100 points
   - Medium Asteroids: 75 points
   - Large Asteroids: 50 points
   - Extra life every two levels (max 5)

4. **Survival Tips**
   - Keep moving - a stationary ship is an easy target
   - Clear asteroids systematically
   - Watch your surroundings when shooting
   - Use screen edges strategically

## For Modders

### Project Structure
```
src/
├── core/          # Core systems and components
├── entities/      # Game entities (ship, asteroids, bullets)
└── ui/           # Menus and UI elements
```

### Quick Modifications

1. **Adjust Game Balance** (`src/core/constants.py`)
   ```python
   # Ship handling
   SHIP_ACCELERATION = 250     # Thrust power
   SHIP_MAX_SPEED = 400       # Top speed
   SHIP_ROTATION_SPEED = 180  # Turn rate
   
   # Bullet properties
   MAX_BULLETS = 12           # Max bullets on screen
   BULLET_SPEED = 800        # Bullet velocity
   BULLET_LIFETIME = 0.5     # Seconds before despawn
   
   # Asteroid properties
   ASTEROID_SPEED_RANGE = (50, 100)  # Min/max speeds
   ```

2. **Modify Particle Effects** (`src/core/particles.py`)
   ```python
   # Thrust particles
   num_particles = random.randint(2, 3)  # Particles per frame
   lifetime = random.uniform(0.2, 0.4)   # Particle duration
   
   # Explosion particles
   num_particles = 24  # For large asteroids
   num_particles = 16  # For medium asteroids
   num_particles = 12  # For small asteroids
   ```

3. **Change Entity Behavior**
   - Ship behavior: `src/entities/ship.py`
   - Asteroid behavior: `src/entities/asteroid.py`
   - Bullet behavior: `src/entities/bullet.py`

### Adding New Features

1. **New Component**
   ```python
   # In src/core/entities/components.py
   class NewComponent(Component):
       def __init__(self, entity):
           super().__init__(entity)
           self.custom_property = initial_value
           
       def update(self):
           # Add update logic here
           pass
   ```

2. **New Entity**
   ```python
   # In src/entities/new_entity.py
   class NewEntity(Entity):
       def __init__(self, game):
           super().__init__(game)
           self.add_component(TransformComponent(self))
           self.add_component(RenderComponent(self))
           # Add other components
   ```

3. **New Game State**
   ```python
   # In src/core/game_state.py
   class GameState(Enum):
       NEW_STATE = auto()
   
   # Add handler method
   def _handle_new_state(self):
       # Add state handling logic
       pass
   ```

### Testing Changes
1. Run the game with your modifications
2. Check the debug output in the console
3. Use the development log to track changes
4. Test all game states and transitions

### Common Issues
1. **Entity not appearing**
   - Check if all required components are added
   - Verify render component initialization
   - Ensure entity is added to game.entities list

2. **Collision not working**
   - Verify collision component radius
   - Check if collision component is active
   - Debug collision detection in game loop

3. **Particles not showing**
   - Confirm particle creation parameters
   - Check particle lifetime values
   - Verify particle component initialization

### Best Practices
1. Follow the existing code style
2. Document your changes
3. Use constants for configuration
4. Test thoroughly before committing
5. Update the development log

For more detailed information, see:
- TECHNICAL_DESIGN.md for architecture details
- GAME_DESIGN_DOCUMENT.md for game specifications
- DEVELOPMENT_LOG.md for change history 