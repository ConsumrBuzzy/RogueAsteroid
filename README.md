# RogueAsteroid

A modern take on the classic Asteroids arcade game, built with Python and Pygame.

## Features

- Component-based entity system
- Smooth physics-based movement
- Particle effects and sound
- High score system
- Multiple control schemes
- Wave-based progression
- Modern menu system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/RogueAsteroid.git
cd RogueAsteroid
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

Start the game by running:
```bash
python src/main.py
```

## Controls

### Arrow Keys (Default)
- ↑: Thrust
- ←/→: Rotate
- SPACE: Shoot
- ESC: Pause/Menu

### WASD Alternative
- W: Thrust
- A/D: Rotate
- SPACE: Shoot
- ESC: Pause/Menu

## Development

### Project Structure
```
RogueAsteroid/
├── assets/
│   ├── sounds/
│   └── images/
├── data/
│   └── highscores.json
├── docs/
│   ├── DEVELOPMENT_LOG.md
│   ├── GAME_DESIGN_DOCUMENT.md
│   └── PROJECT_CHARTER.md
├── src/
│   ├── core/
│   │   ├── entities/
│   │   ├── audio.py
│   │   ├── constants.py
│   │   ├── game.py
│   │   ├── highscores.py
│   │   └── particles.py
│   ├── entities/
│   │   ├── asteroid.py
│   │   ├── bullet.py
│   │   └── ship.py
│   ├── ui/
│   │   └── menus.py
│   └── main.py
├── tests/
│   ├── test_components.py
│   ├── test_entities.py
│   └── test_integration.py
├── README.md
└── requirements.txt
```

### Running Tests

Run the test suite with:
```bash
python -m unittest discover tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original Asteroids game by Atari
- Pygame community
- Sound effects from [source]
- Inspiration from modern arcade games 