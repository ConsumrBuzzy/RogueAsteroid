class HighScoreManager:
    def __init__(self, game):
        self.logger = get_logger()
        self.game = game
        self.high_scores = []
        self.current_score = 0
        self.load_high_scores()

    def add_high_score(self, player_name: str) -> None:
        """Add a new high score entry."""
        self.logger.info(f"Adding high score: {self.current_score} by {player_name}")
        # Create new score entry
        new_score = {
            'name': player_name,
            'score': self.current_score,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        # Add to list and sort
        self.high_scores.append(new_score)
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Keep only top 10
        self.high_scores = self.high_scores[:10]
        
        # Save to file
        self.save_high_scores()
        self.logger.info("High score saved successfully") 