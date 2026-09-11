import pygame
from pygame.sprite import Sprite


class AlienBullet(Sprite):
    """A class to manage bullets fired by aliens."""

    def __init__(self, ai_game, alien):
        """Create an alien bullet at the alien's position."""
        super().__init__()

        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.alien_bullet_color

        # Create a bullet rectangle.
        self.rect = pygame.Rect(
            0, 0,
            self.settings.alien_bullet_width,
            self.settings.alien_bullet_height
        )

        # Start the bullet below the alien.
        self.rect.midtop = alien.rect.midbottom

        # Store the bullet's exact vertical position.
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet down the screen."""
        self.y += self.settings.alien_bullet_speed
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the alien bullet to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)