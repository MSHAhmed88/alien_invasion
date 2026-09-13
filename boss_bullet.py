import pygame
from pygame.sprite import Sprite


class BossBullet(Sprite):
    """A class to manage bullets fired by the boss."""

    def __init__(self, ai_game, boss):
        """Create a boss bullet at the boss's position."""
        super().__init__()

        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = (255, 0, 255)

        self.rect = pygame.Rect(
            0,
            0,
            8,
            25
        )

        self.rect.midtop = boss.rect.midbottom

        self.y = float(self.rect.y)

    def update(self):
        """Move the boss bullet down the screen."""
        self.y += 4.0
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the boss bullet."""
        pygame.draw.rect(
            self.screen,
            self.color,
            self.rect
        )
        