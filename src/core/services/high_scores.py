"""High score management system."""
from src.core.logging import get_logger

class HighScoreManager:
    """Manages high scores for the game."""
    
    def __init__(self):
        """Initialize the high scores system."""
        self.logger = get_logger()
        self.scores = []  # List of (name, score) tuples
        self.max_scores = 10
        self.logger.info("High score manager initialized")
        self.load_scores()
    
    def load_scores(self):
        """Load high scores from file."""
        try:
            with open('data/high_scores.txt', 'r') as f:
                for line in f:
                    try:
                        name, score = line.strip().split(',')
                        score = int(score)  # Ensure score is an integer
                        self.scores.append((name, score))
                    except ValueError:
                        self.logger.warning(f"Invalid score entry: {line.strip()}")
                        continue
            self.logger.info(f"Loaded {len(self.scores)} high scores")
        except FileNotFoundError:
            self.logger.info("No high scores file found, creating new one")
            self._ensure_data_dir()
            self.save_scores()  # Create empty file
    
    def save_scores(self):
        """Save high scores to file."""
        self._ensure_data_dir()
        try:
            with open('data/high_scores.txt', 'w') as f:
                for name, score in self.scores:
                    f.write(f"{name},{score}\n")
            self.logger.debug(f"Saved {len(self.scores)} high scores")
        except Exception as e:
            self.logger.error(f"Error saving high scores: {e}")
    
    def add_score(self, name: str, score: int):
        """Add a new high score."""
        self.logger.info(f"Adding score: {name} - {score}")
        try:
            score = int(score)  # Ensure score is an integer
            self.scores.append((name, score))
            # Sort by the score value (second element of tuple)
            self.scores.sort(key=lambda x: int(x[1]), reverse=True)
            self.scores = self.scores[:self.max_scores]  # Keep only top scores
            self.save_scores()
            self.logger.debug(f"Score added successfully. Current scores: {self.scores}")
        except Exception as e:
            self.logger.error(f"Error adding score: {e}")
    
    def get_scores(self):
        """Get the list of high scores."""
        return self.scores
    
    def is_high_score(self, score: int) -> bool:
        """Check if a score qualifies as a high score."""
        try:
            score = int(score)  # Ensure score is an integer
            if len(self.scores) < self.max_scores:
                self.logger.debug(f"Score {score} qualifies (fewer than {self.max_scores} scores)")
                return True
            is_high = score > self.scores[-1][1] if self.scores else True
            if is_high:
                self.logger.debug(f"Score {score} qualifies (beats lowest score {self.scores[-1][1]})")
            return is_high
        except Exception as e:
            self.logger.error(f"Error checking high score: {e}")
            return False
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists."""
        import os
        os.makedirs('data', exist_ok=True)
        self.logger.debug("Ensured data directory exists") 