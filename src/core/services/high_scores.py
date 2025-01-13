class HighScores:
    """Manages high scores for the game."""
    
    def __init__(self, game):
        """Initialize the high scores system."""
        self.game = game
        self.scores = []  # List of (name, score) tuples
        self.max_scores = 10
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
                        print(f"Invalid score entry: {line.strip()}")  # Debug info
                        continue
        except FileNotFoundError:
            print("No high scores file found, creating new one")  # Debug info
            self._ensure_data_dir()
            self.save_scores()  # Create empty file
    
    def save_scores(self):
        """Save high scores to file."""
        self._ensure_data_dir()
        with open('data/high_scores.txt', 'w') as f:
            for name, score in self.scores:
                f.write(f"{name},{score}\n")
    
    def add_score(self, name: str, score: int):
        """Add a new high score."""
        print(f"Adding score: {name} - {score}")  # Debug info
        try:
            score = int(score)  # Ensure score is an integer
            self.scores.append((name, score))
            # Sort by the score value (second element of tuple)
            self.scores.sort(key=lambda x: int(x[1]), reverse=True)
            self.scores = self.scores[:self.max_scores]  # Keep only top scores
            self.save_scores()
            print(f"Score added successfully. Current scores: {self.scores}")  # Debug info
        except Exception as e:
            print(f"Error adding score: {e}")  # Debug info
    
    def get_scores(self):
        """Get the list of high scores."""
        return self.scores
    
    def is_high_score(self, score: int) -> bool:
        """Check if a score qualifies as a high score."""
        try:
            score = int(score)  # Ensure score is an integer
            if len(self.scores) < self.max_scores:
                return True
            return score > self.scores[-1][1] if self.scores else True
        except Exception as e:
            print(f"Error checking high score: {e}")  # Debug info
            return False
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists."""
        import os
        os.makedirs('data', exist_ok=True) 