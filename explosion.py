import pygame
from pygame.sprite import Sprite


class Explosion(Sprite):
    """A class to display an explosion."""

    def __init__(self, ai_game, alien):
        """Create an explosion at the alien's position."""
        super().__init__()

        self.screen = ai_game.screen

        self.image = pygame.image.load('images/explosion.png')
        self.image = pygame.transform.scale(self.image, (70, 70))

        self.rect = self.image.get_rect()
        self.rect.center = alien.rect.center

        self.timer = 200

    def update(self):
        """Keep the explosion on screen briefly."""
        self.timer -= 1000 / 60

        if self.timer <= 0:
            self.kill()

    def draw(self):
        """Draw the explosion."""
        self.screen.blit(self.image, self.rect)