import pygame
import sys
from typing import List
from .constants import *
from .entity import Entity
from ..entities.ship import Ship

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
        
        # Time tracking
        self.dt = 0  # delta time in seconds
        
        # Create player ship
        self.player = Ship()
        self.add_entity(self.player)
    
    def run(self) -> None:
        """Main game loop."""
        self.running = True
        
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            self._handle_events()
            self._handle_input()
            
            if not self.paused:
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
                    self.paused = not self.paused
    
    def _handle_input(self) -> None:
        """Process continuous keyboard input."""
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