# RogueAsteroid - Game Design Document

## Game Overview
RogueAsteroid is a classic arcade-style space shooter where players pilot a ship through waves of asteroids. The game features precise controls, physics-based movement, and particle effects for visual feedback. The focus is on skill-based gameplay with increasing difficulty as players progress through levels.

## Core Gameplay Elements

### Player Ship
- Movement Mechanics:
  * Thrust-based movement with gradual acceleration/deceleration
  * Maximum speed of 400 pixels/second
  * Rotation speed of 180 degrees/second
  * Screen wrapping for continuous play space
- Weapons:
  * Single forward-firing bullet type
  * Maximum of 12 bullets on screen
  * 0.5 second bullet lifetime
  * Visual feedback with particle effects

### Asteroids
- Types:
  * Large: 50 points, splits into 2 medium
  * Medium: 75 points, splits into 2 small
  * Small: 100 points, destroyed completely
- Mechanics:
  * Random movement paths with consistent velocity
  * Screen wrapping
  * Arcade-style collisions with deflection
  * Size-based collision radius
  * Particle effects on destruction

### Scoring System
- Point Values:
  * Small Asteroids: 100 points
  * Medium Asteroids: 75 points
  * Large Asteroids: 50 points
- High Score:
  * Top 5 scores saved
  * Player name entry for high scores
  * Scores saved between sessions

## Visual Design

### Art Style
- Vector-based graphics
- Particle effects for:
  * Ship thrust
  * Bullet impacts
  * Asteroid destruction
  * Asteroid splitting
- Color scheme:
  * Ship: White
  * Bullets: White
  * Asteroids: White
  * Thrust particles: Blue-white
  * Explosion particles: Orange/yellow
  * UI text: White

### UI Elements
- HUD:
  * Score display (top left)
  * Lives counter (below score)
  * Level indicator (top right)
- Menus:
  * Main Menu: New Game, High Scores, Options, Quit
  * Pause Menu: Resume, Options, Main Menu
  * Options: Control scheme toggle (Arrows/WASD)
  * Game Over: Score, Level, High Score status

## Game Flow
- States:
  * MAIN_MENU: Starting state
  * PLAYING: Active gameplay
  * PAUSED: Game paused
  * GAME_OVER: End state
  * NEW_HIGH_SCORE: Score entry
  * OPTIONS: Settings menu
- Levels:
  * Progressive difficulty
  * Extra life every two levels (max 5)
  * Increasing number of asteroids
  * Faster asteroid velocities

## Technical Requirements
- Python with Pygame
- 60 FPS target
- Smooth particle effects
- Responsive controls
- Efficient collision detection
- State-based game management

## Success Metrics
- Smooth, responsive controls
- Clear visual feedback
- Progressive difficulty
- Engaging score system
- Polished particle effects
- Clean state transitions

Note: This document reflects the current implementation. Future updates may include sound effects and additional gameplay features. 