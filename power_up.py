import pygame
from pygame.sprite import Sprite


class PowerUp(Sprite):
    """A class to represent a power-up."""

    def __init__(self, ai_game, power_up_type):
        """Create a power-up."""
        super().__init__()

        self.screen = ai_game.screen
        self.settings = ai_game.settings

        self.power_up_type = power_up_type

        self.rect = pygame.Rect(
            0,
            0,
            30,
            30
        )

        self.rect.center = (0, 0)

        self.y = float(self.rect.y)

    def update(self):
        """Move the power-up down the screen."""
        self.y += 2.0
        self.rect.y = self.y

        # Remove the power-up if it leaves the screen.
        if self.rect.top > self.settings.screen_height:
            self.kill()

    def draw(self):
        """Draw the power-up."""
        if self.power_up_type == "health":
            pygame.draw.rect(
                self.screen,
                (0, 200, 0),
                self.rect
            )

            # Draw a white plus sign.
            center_x = self.rect.centerx
            center_y = self.rect.centery

            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                (center_x - 3, center_y - 10, 6, 20)
            )

            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                (center_x - 10, center_y - 3, 20, 6)
            )

        elif self.power_up_type == "rapid_fire":
            pygame.draw.rect(
                self.screen,
                (255, 200, 0),
                self.rect
            )

            # Draw a white lightning bolt.
            center_x = self.rect.centerx
            center_y = self.rect.centery

            pygame.draw.polygon(
                self.screen,
                (255, 255, 255),
                [
                    (center_x + 3, center_y - 12),
                    (center_x - 8, center_y + 2),
                    (center_x - 1, center_y + 2),
                    (center_x - 4, center_y + 12),
                    (center_x + 8, center_y - 3),
                    (center_x + 1, center_y - 3),
                ]
            )

        elif self.power_up_type == "shield":
            pygame.draw.circle(
                self.screen,
                (0, 150, 255),
                self.rect.center,
                15,
                3
            )

            # Draw a white shield symbol.
            center_x = self.rect.centerx
            center_y = self.rect.centery

            pygame.draw.polygon(
                self.screen,
                (255, 255, 255),
                [
                    (center_x, center_y - 10),
                    (center_x - 8, center_y - 5),
                    (center_x - 6, center_y + 5),
                    (center_x, center_y + 10),
                    (center_x + 6, center_y + 5),
                    (center_x + 8, center_y - 5),
                ]
            )