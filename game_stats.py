class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """Initialise statistics."""
        self.settings = ai_game.settings 
        self.reset_stats()
        #high score should never be reset.
        self.high_scores = [0, 0, 0]

    def reset_stats(self):
        """Initialise statistics that can change during the game."""
        self.ship_health = self.settings.ship_health
        self.score = 0
        self.level = 1