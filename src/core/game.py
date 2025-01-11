import pygame
import sys
import numpy as np
from typing import List
from src.core.constants import *
from src.core.entity import Entity
from src.core.settings import Settings
from src.core.menu import MainMenu, OptionsMenu
from src.core.spawner import Spawner
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid

class Game:
    """Main game class handling the game loop and state management."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        
        self.clock = pygame.time.Clock()
        self.running = False
        self.paused = False
        
        # Game state
        self.score = 0
        self.lives = INITIAL_LIVES
        self.entities: List[Entity] = []
        self.settings = Settings()
        
        # Menu system
        self.current_menu = None
        self.in_menu = True
        self.main_menu = MainMenu(self)
        self.options_menu = OptionsMenu(self)
        
        # Time tracking
        self.dt = 0  # delta time in seconds
        
        # Create player ship
        self.player = None
        
        # Create spawner
        self.spawner = Spawner(self)
        self.wave_transition = False
        self.wave_transition_timer = 0.0
        self.WAVE_TRANSITION_DELAY = 2.0  # seconds
    
    def run(self) -> None:
        """Main game loop."""
        self.running = True
        self.show_main_menu()
        
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            self._handle_events()
            
            if not self.paused:
                if self.in_menu:
                    self.current_menu.update()
                else:
                    self._handle_input()
                    self._update()
            
            self._render()
            
        pygame.quit()
        sys.exit()
    
    def _handle_events(self) -> None:
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.in_menu:
                        if isinstance(self.current_menu, OptionsMenu):
                            self.show_main_menu()
                    else:
                        self.paused = not self.paused
            
            if self.in_menu:
                self.current_menu.handle_input(event)
    
    def _handle_input(self) -> None:
        """Process continuous keyboard input."""
        if self.player:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
    
    def _update(self) -> None:
        """Update game state."""
        # Update spawner
        if not self.wave_transition:
            self.spawner.update(self.dt)
            
            # Check for wave completion
            if self.spawner.check_wave_complete():
                self.wave_transition = True
                self.wave_transition_timer = 0.0
        else:
            # Handle wave transition
            self.wave_transition_timer += self.dt
            if self.wave_transition_timer >= self.WAVE_TRANSITION_DELAY:
                self.wave_transition = False
                self.spawner.advance_wave()
        
        # Update all entities
        for entity in self.entities:
            if entity.active:
                entity.update(self.dt)
        
        # Check collisions
        self._check_collisions()
        
        # Clean up inactive entities
        self.entities = [e for e in self.entities if e.active]
    
    def _check_collisions(self) -> None:
        """Check for collisions between entities."""
        n = len(self.entities)
        for i in range(n):
            if not self.entities[i].active:
                continue
            for j in range(i + 1, n):
                if not self.entities[j].active:
                    continue
                    
                entity1 = self.entities[i]
                entity2 = self.entities[j]
                
                if entity1.collides_with(entity2):
                    # Handle ship-asteroid collisions
                    if isinstance(entity1, Ship) and isinstance(entity2, Asteroid):
                        self._handle_ship_collision(entity1, entity2)
                    elif isinstance(entity1, Asteroid) and isinstance(entity2, Ship):
                        self._handle_ship_collision(entity2, entity1)
    
    def _handle_ship_collision(self, ship: Ship, asteroid: Asteroid) -> None:
        """Handle collision between ship and asteroid."""
        if self.lives > 0:
            self.lives -= 1
            ship.position = np.array([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
            ship.velocity = np.array([0.0, 0.0])
            ship.rotation = 0.0
        else:
            self.show_main_menu()
    
    def _render(self) -> None:
        """Render the game state."""
        if self.in_menu:
            self.current_menu.draw(self.screen)
        else:
            # Clear screen
            self.screen.fill(BLACK)
            
            # Draw all entities
            for entity in self.entities:
                if entity.active:
                    entity.draw(self.screen)
            
            # Draw wave transition
            if self.wave_transition:
                font = pygame.font.Font(None, 64)
                text = f"Wave {self.spawner.wave + 1}"
                text_surface = font.render(text, True, WHITE)
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
                self.screen.blit(text_surface, text_rect)
            
            # Draw HUD
            self._draw_hud()
        
        # Update display
        pygame.display.flip()
    
    def _draw_hud(self) -> None:
        """Draw heads-up display."""
        font = pygame.font.Font(None, 36)
        
        # Draw score
        score_text = f"Score: {self.score}"
        score_surface = font.render(score_text, True, WHITE)
        self.screen.blit(score_surface, (10, 10))
        
        # Draw lives
        lives_text = f"Lives: {self.lives}"
        lives_surface = font.render(lives_text, True, WHITE)
        self.screen.blit(lives_surface, (10, 50))
        
        # Draw wave
        wave_text = f"Wave: {self.spawner.wave}"
        wave_surface = font.render(wave_text, True, WHITE)
        wave_rect = wave_surface.get_rect()
        wave_rect.right = WINDOW_WIDTH - 10
        wave_rect.top = 10
        self.screen.blit(wave_surface, wave_rect)
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the game."""
        entity.game = self  # Set reference to game
        self.entities.append(entity)
    
    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the game."""
        entity.active = False
    
    # Menu management methods
    def show_main_menu(self) -> None:
        """Show the main menu."""
        self.current_menu = self.main_menu
        self.in_menu = True
    
    def show_options(self) -> None:
        """Show the options menu."""
        self.current_menu = self.options_menu
        self.in_menu = True
    
    def start_game(self) -> None:
        """Start a new game."""
        self.in_menu = False
        self.paused = False
        self.entities.clear()
        self.score = 0
        self.lives = INITIAL_LIVES
        
        # Reset wave system
        self.spawner = Spawner(self)
        self.wave_transition = False
        self.wave_transition_timer = 0.0
        
        # Create player
        self.player = Ship()
        self.add_entity(self.player)
        
        # Start first wave
        self.spawner.start_wave() 