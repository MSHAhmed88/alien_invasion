import pygame
from pygame.sprite import Sprite


class Boss(Sprite):
    """A class to manage the boss alien."""

    def __init__(self, ai_game):
        """Initialise the boss."""
        super().__init__()

        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.health = self.settings.boss_health

        # Load the boss image.
        self.image = pygame.image.load('images/boss.png')
        self.image = pygame.transform.scale(self.image, (300, 300))

        # Get the boss rectangle.
        self.rect = self.image.get_rect()

        # Start the boss at the top-centre of the screen.
        self.rect.midtop = (
            self.screen.get_rect().centerx,
            30
        )

        # Store a floating-point x position.
        self.x = float(self.rect.x)
        self.speed = 3.0
        self.direction = 1

    def draw_health_bar(self):
        """Draw the boss health bar."""
        bar_width = 300
        bar_height = 20

        health_ratio = self.health / self.settings.boss_health

        # Background.
        pygame.draw.rect(
            self.screen,
            (100, 100, 100),
            (self.rect.left, self.rect.top - 30,
            bar_width, bar_height)
        )

        # Current health.
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            (self.rect.left, self.rect.top - 30,
            bar_width * health_ratio, bar_height)
        )

        # Border.
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (self.rect.left, self.rect.top - 30,
            bar_width, bar_height),
            2
        )

    def update(self):
        """Move the boss from side to side."""
        self.x += self.speed * self.direction
        self.rect.x = self.x

        # Reverse direction at the screen edges.
        if self.rect.right >= self.screen.get_rect().right:
            self.direction = -1
        elif self.rect.left <= 0:
            self.direction = 1