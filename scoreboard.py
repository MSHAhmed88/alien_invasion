import pygame.font
from pygame.sprite import Group
from ship import Ship

class Scoreboard:
    """A class to report scoring information."""

    def __init__(self, ai_game):
        """Initializing scorekeeping attributes."""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        #font settings for scoring information.
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 48)
        self.game_over_font = pygame.font.SysFont(None, 72)

        #prepare the initial score images.
        self.prep_score()
        self.prep_high_scores()
        self.prep_level()

    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = round(self.stats.score, -1)
        score_str = f"{rounded_score:,}"
        self.score_image = self.font.render(score_str, True,
                self.text_color, self.settings.bg_color)

        #display the score at the top right of the screen.
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_scores(self):
        """Turn the top 3 scores into rendered images."""
        self.high_score_images = []
        self.high_score_rects = []

        for rank, score in enumerate(self.stats.high_scores):
            score_str = f"{score:,}"
            score_image = self.font.render(
                f"{rank + 1}. {score_str}",
                True,
                self.text_color,
                self.settings.bg_color
            )

            score_rect = score_image.get_rect()
            score_rect.centerx = self.screen_rect.centerx
            score_rect.top = 20 + (rank * 50)

            self.high_score_images.append(score_image)
            self.high_score_rects.append(score_rect)

    def prep_level(self):
        """Turn the level into a rendered image."""
        level_str = str(self.stats.level)
        self.level_image = self.font.render(level_str, True,
                self.text_color, self.settings.bg_color)

        #position the level below the score.
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def show_score(self):
        """Draw scores, level and ships to the screen."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.level_image, self.level_rect)

    def show_high_scores(self):
        """Draw the top 3 scores to the screen."""
        for score_image, score_rect in zip(
                self.high_score_images, self.high_score_rects):
            self.screen.blit(score_image, score_rect)

    def update_high_scores(self):
        """Add the current score to the top 3 scores."""
        self.stats.high_scores.append(self.stats.score)

        # Sort from highest to lowest.
        self.stats.high_scores.sort(reverse=True)

        # Keep only the top 3 scores.
        self.stats.high_scores = self.stats.high_scores[:3]

        # Prepare the new score images.
        self.prep_high_scores()

    def show_health_bar(self):
        """Draw the ship's health bar."""
        health_ratio = self.stats.ship_health / self.settings.ship_health
        health_text = f"Health: {self.stats.ship_health}%"

        health_image = self.font.render(
            health_text,
            True,
            self.text_color,
            self.settings.bg_color
        )

        health_rect = health_image.get_rect()
        health_rect.left = 20
        health_rect.bottom = 45

        self.screen.blit(health_image, health_rect)

        # Draw the health bar background.
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            (20, 55, self.settings.health_bar_width,
            self.settings.health_bar_height)
        )

        if self.stats.ship_health >= 60:
            health_color = (0, 255, 0)
        elif self.stats.ship_health >= 30:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)

        # Draw the remaining health.
        pygame.draw.rect(
            self.screen,
            health_color,
            (20, 55,
            self.settings.health_bar_width * health_ratio,
            self.settings.health_bar_height)
        )

        # Draw a border around the health bar.
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (20, 55, self.settings.health_bar_width,
            self.settings.health_bar_height),
            2
        )

    def show_game_over(self):
        """Display the game-over information."""
        game_over_image = self.game_over_font.render(
            "GAME OVER",
            True,
            self.text_color,
            self.settings.bg_color
        )

        game_over_rect = game_over_image.get_rect()
        game_over_rect.centerx = self.screen_rect.centerx
        game_over_rect.top = 100

        self.screen.blit(game_over_image, game_over_rect)

    def show_game_over_stats(self):
        """Display the final game statistics."""
        stats = [
            f"Final Score: {self.stats.score:,}",
            f"Level Reached: {self.stats.level}",
            f"Aliens Destroyed: {self.stats.aliens_destroyed}",
        ]

        for index, text in enumerate(stats):
            stats_image = self.font.render(
                text,
                True,
                self.text_color,
                self.settings.bg_color
            )

            stats_rect = stats_image.get_rect()
            stats_rect.centerx = self.screen_rect.centerx
            stats_rect.top = 200 + (index * 50)

            self.screen.blit(stats_image, stats_rect)

    