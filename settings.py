class Settings:
    """A class to store all settings for Alien Invasion"""

    def __init__(self):
        """Initialising the game's static settings"""
        #screen settings.
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)

        #ship settings
        self.ship_health = 100
        self.health_bar_width = 200
        self.health_bar_height = 20
        self.ship_invulnerability_time = 5000

        #bullet settings
        self.bullet_width = 4
        self.bullet_height = 20
        self.bullet_color = (255, 255, 255)
        self.bullets_allowed = 100

        #Alien settings
        self.fleet_drop_speed = 30
        self.alien_shot_interval = 2000

        #alien bullet settings
        self.alien_bullet_speed = 2.5
        self.alien_bullet_width = 4
        self.alien_bullet_height = 15
        self.alien_bullet_color = (255, 0, 0)

        #how quickly the game speeds up.
        self.speedup_scale = 1.2
        #how quickly the alien point valie increases.
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 3
        self.bullet_speed = 3
        self.alien_speed = 1.0

        #fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        #scoring settings.
        self.alien_points = 10

    def increase_speed(self):
        """Increase speed settings and alien point values."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)