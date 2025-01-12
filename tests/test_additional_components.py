"""Tests for additional components."""
import pytest
import pygame
from pygame import Surface, Vector2
from typing import Tuple

from src.core.entities.base import Entity
from src.core.components import (
    TransformComponent,
    PhysicsComponent,
    EffectComponent,
    WaveComponent,
    UIComponent,
    TimerComponent,
    ScoreComponent,
    HealthComponent,
    DebugComponent,
    AudioComponent
)

@pytest.fixture
def mock_game():
    """Create a mock game instance for testing."""
    class MockGame:
        def __init__(self):
            self.screen = Surface((800, 600))
            self.dt = 0.016
    return MockGame()

@pytest.fixture
def entity(mock_game):
    """Create a test entity."""
    return Entity(mock_game)

@pytest.mark.unit
class TestWaveComponent:
    """Test cases for WaveComponent."""
    
    def test_wave_init(self, entity):
        """Test wave component initialization."""
        wave = WaveComponent(entity)
        assert wave.current_wave == 1
        assert wave.enemies_remaining == 0
        assert wave.wave_complete is False
        
    def test_wave_progression(self, entity):
        """Test wave progression mechanics."""
        wave = WaveComponent(entity)
        wave.start_wave()
        
        # First wave should have base enemies
        initial_enemies = wave.enemies_remaining
        assert initial_enemies > 0
        
        # Complete wave
        for _ in range(initial_enemies):
            wave.enemy_destroyed()
            
        assert wave.wave_complete is True
        assert wave.enemies_remaining == 0
        
        # Next wave
        wave.next_wave()
        assert wave.current_wave == 2
        assert wave.enemies_remaining > initial_enemies
        assert wave.wave_complete is False
        
    def test_wave_callbacks(self, entity):
        """Test wave event callbacks."""
        wave = WaveComponent(entity)
        wave_start_called = False
        wave_complete_called = False
        
        def on_wave_start(wave_num, enemies, multiplier):
            nonlocal wave_start_called
            wave_start_called = True
            assert wave_num == 1
            assert enemies > 0
            assert multiplier == 1.0
            
        def on_wave_complete(wave_num):
            nonlocal wave_complete_called
            wave_complete_called = True
            assert wave_num == 1
            
        wave.register_callback('on_wave_start', on_wave_start)
        wave.register_callback('on_wave_complete', on_wave_complete)
        
        wave.start_wave()
        assert wave_start_called is True
        
        # Complete wave
        while wave.enemies_remaining > 0:
            wave.enemy_destroyed()
            
        assert wave_complete_called is True
        
    def test_difficulty_scaling(self, entity):
        """Test difficulty scaling between waves."""
        wave = WaveComponent(entity, difficulty_multiplier=1.5)
        initial_scale = wave.get_difficulty_scale()
        assert initial_scale == 1.0
        
        wave.next_wave()
        assert wave.get_difficulty_scale() == 1.5
        
        wave.next_wave()
        assert wave.get_difficulty_scale() == 2.25  # 1.5^2
        
    def test_wave_reset(self, entity):
        """Test wave reset functionality."""
        wave = WaveComponent(entity)
        wave.start_wave()
        wave.next_wave()
        wave.next_wave()
        
        assert wave.current_wave == 3
        
        wave.reset_waves()
        assert wave.current_wave == 1
        assert wave.enemies_remaining == 0
        assert wave.wave_complete is False

@pytest.mark.unit
class TestEffectComponent:
    """Test cases for EffectComponent."""
    
    def test_effect_init(self, entity):
        """Test EffectComponent initialization."""
        effect = EffectComponent(entity)
        assert effect.entity == entity
        assert effect.effects == {}
    
    def test_effect_creation(self, entity):
        """Test effect creation and properties."""
        effect = EffectComponent(entity)
        vertices = [(0, 0), (10, 0), (5, 10)]
        color = (255, 0, 0)
        offset = Vector2(5, 5)
        
        effect.add_effect('test', vertices, color, offset)
        created_effect = effect.effects.get('test')
        assert created_effect is not None
        assert created_effect.vertices == vertices
        assert created_effect.color == color
        assert created_effect.offset == offset
        assert not created_effect.active 

@pytest.mark.unit
class TestScoreComponent:
    """Test cases for ScoreComponent."""
    
    def test_score_init(self, entity):
        """Test score component initialization."""
        score = ScoreComponent(entity)
        assert score.current_score == 0
        assert score.high_scores == []
        assert score.score_multiplier == 1.0
        
    def test_score_points(self, entity):
        """Test adding points with multiplier."""
        score = ScoreComponent(entity)
        
        # Base points
        score.add_points(100)
        assert score.current_score == 100
        
        # With multiplier
        score.set_multiplier(2.0)
        score.add_points(100)
        assert score.current_score == 300  # 100 + (100 * 2)
        
        # Event tracking
        score.add_points(50, "asteroid")
        assert score.get_score_breakdown()["asteroid"] == 100  # 50 * 2
        
    def test_high_scores(self, entity):
        """Test high score management."""
        score = ScoreComponent(entity, max_high_scores=3)
        
        # Add scores
        score.current_score = 100
        assert score.add_high_score("Player1")
        
        score.current_score = 200
        assert score.add_high_score("Player2")
        
        score.current_score = 50
        assert score.add_high_score("Player3")
        
        # Check ordering
        assert len(score.high_scores) == 3
        assert score.high_scores[0] == ("Player2", 200)
        assert score.high_scores[1] == ("Player1", 100)
        assert score.high_scores[2] == ("Player3", 50)
        
        # Add higher score
        score.current_score = 300
        assert score.add_high_score("Player4")
        assert len(score.high_scores) == 3  # Still 3 due to max_high_scores
        assert score.high_scores[0] == ("Player4", 300)
        
    def test_score_reset(self, entity):
        """Test score reset functionality."""
        score = ScoreComponent(entity)
        
        score.add_points(100, "asteroid")
        score.set_multiplier(2.0)
        
        score.reset_score()
        assert score.current_score == 0
        assert score.score_multiplier == 1.0
        assert score.get_score_breakdown() == {}
        
    def test_high_score_check(self, entity):
        """Test high score qualification check."""
        score = ScoreComponent(entity, max_high_scores=2)
        
        # First score always qualifies
        score.current_score = 100
        assert score.is_high_score()
        score.add_high_score("Player1")
        
        # Higher score qualifies
        score.current_score = 200
        assert score.is_high_score()
        score.add_high_score("Player2")
        
        # Lower score doesn't qualify
        score.current_score = 50
        assert not score.is_high_score()
        
        # Equal score doesn't qualify
        score.current_score = 100
        assert not score.is_high_score()
        
        # Clear high scores
        score.clear_high_scores()
        assert len(score.high_scores) == 0
        assert score.is_high_score()  # Any score qualifies when list is empty 