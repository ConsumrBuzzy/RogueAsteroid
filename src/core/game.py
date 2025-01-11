import pygame
import sys
from typing import List
from .constants import *
from .entity import Entity
from .settings import Settings
from .menu import MainMenu, OptionsMenu
from entities.ship import Ship

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
                if self.entities[i].collides_with(self.entities[j]):
                    # Handle collision (to be implemented in derived classes)
                    pass
    
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
        
        # Update display
        pygame.display.flip()
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the game."""
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
        
        # Create player
        self.player = Ship()
        self.add_entity(self.player) 