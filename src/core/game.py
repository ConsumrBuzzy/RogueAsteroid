"""Core game loop and state management."""
import pygame
import numpy as np
from typing import List, Optional, Dict, Any
from src.core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    BLACK,
    INITIAL_LIVES
)
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.ui.menus import MainMenu, OptionsMenu
from src.core.audio import AudioManager
from src.core.particles import ParticleSystem

class GameState:
    """Game state management."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class Game:
    """Main game class managing entities and game loop."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Rogue Asteroid")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        self.dt = 0.0
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        
        # Settings with defaults
        self.settings: Dict[str, Any] = {
            'controls': {
                'scheme': 'arrows'  # or 'wasd'
            }
        }
        
        # Entity management
        self.entities: List[Any] = []
        self.ship: Optional[Ship] = None
        self.asteroids: List[Asteroid] = []
        
        # Systems
        self.audio = AudioManager()
        self.particles = ParticleSystem()
        
        # UI
        self.main_menu = MainMenu(self)
        self.options_menu = OptionsMenu(self)
    
    def reset_game(self) -> None:
        """Reset game state for new game."""
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        self.entities.clear()
        self.asteroids.clear()
        self.particles.clear()
        
        # Create player ship
        self.ship = Ship(self)
        self.entities.append(self.ship)
        
        # Spawn initial asteroids
        self.spawn_asteroid_wave()
    
    def spawn_asteroid_wave(self) -> None:
        """Spawn a wave of asteroids based on current level."""
        num_asteroids = 2 + self.level
        
        for _ in range(num_asteroids):
            # Spawn asteroids away from player
            while True:
                x = np.random.uniform(0, WINDOW_WIDTH)
                y = np.random.uniform(0, WINDOW_HEIGHT)
                
                if self.ship:
                    dist = np.hypot(x - self.ship.get_component('transform').position[0],
                                  y - self.ship.get_component('transform').position[1])
                    if dist > 200:  # Minimum safe distance
                        break
                else:
                    break
            
            asteroid = Asteroid(self, x, y, 'large')
            self.asteroids.append(asteroid)
            self.entities.append(asteroid)
    
    def handle_collisions(self) -> None:
        """Handle collisions between entities."""
        if not self.ship or self.state != GameState.PLAYING:
            return
            
        ship_collision = self.ship.get_component('collision')
        if not ship_collision:
            return
            
        # Check ship collision with asteroids
        for asteroid in self.asteroids[:]:  # Copy list for safe removal
            asteroid_collision = asteroid.get_component('collision')
            if not asteroid_collision:
                continue
                
            if ship_collision.collides_with(asteroid_collision):
                self.lives -= 1
                
                # Create explosion effect
                transform = self.ship.get_component('transform')
                if transform:
                    self.particles.create_explosion(
                        transform.position,
                        (255, 0, 0),  # Red explosion
                        num_particles=30,
                        speed_range=(100, 200)
                    )
                    self.audio.play_sound('explosion_large')
                
                self.entities.remove(self.ship)
                self.ship = None
                
                if self.lives > 0:
                    # Respawn ship after delay
                    self.ship = Ship(self)
                    self.entities.append(self.ship)
                else:
                    self.state = GameState.GAME_OVER
                break
    
    def update(self) -> None:
        """Update game state and entities."""
        self.dt = self.clock.tick(FPS) / 1000.0
        
        if self.state == GameState.MENU:
            self.main_menu.update()
        elif self.state == GameState.PLAYING:
            # Update all entities
            for entity in self.entities[:]:  # Copy list for safe removal
                entity.update(self.dt)
            
            # Update particles
            self.particles.update(self.dt)
            
            # Handle collisions
            self.handle_collisions()
            
            # Check for level completion
            if not self.asteroids and self.ship:
                self.level += 1
                self.spawn_asteroid_wave()
    
    def draw(self) -> None:
        """Draw current game state."""
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.main_menu.draw(self.screen)
        elif self.state == GameState.OPTIONS:
            self.options_menu.draw(self.screen)
        elif self.state in [GameState.PLAYING, GameState.PAUSED]:
            # Draw all entities
            for entity in self.entities:
                entity.draw(self.screen)
            
            # Draw particles
            self.particles.draw(self.screen)
            
            # Draw HUD
            self._draw_hud()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        
        pygame.display.flip()
    
    def _draw_hud(self) -> None:
        """Draw heads-up display."""
        font = pygame.font.Font(None, 36)
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 50))
        
        # Draw level
        level_text = font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (WINDOW_WIDTH - 120, 10))
    
    def _draw_game_over(self) -> None:
        """Draw game over screen."""
        font = pygame.font.Font(None, 74)
        text = font.render('Game Over', True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.screen.blit(text, text_rect)
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Final Score: {self.score}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))
        self.screen.blit(score_text, score_rect)
    
    def run(self) -> None:
        """Main game loop."""
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.PAUSED
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING
            
            self.update()
            self.draw()
        
        pygame.quit() 