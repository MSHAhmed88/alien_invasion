import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button 
from ship import Ship
from bullet import Bullet
from alien import Alien
from alien_bullet import AlienBullet
from explosion import Explosion

class AlienInvasion:
    """Overall class to manage game assets and behaviour"""

    def __init__(self):
        """Initialising the game, and create resources"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # Hide the mouse cursor initially.
        pygame.mouse.set_visible(True)

        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        
        pygame.display.set_caption("Alien Invasion")

        #create an instance to store game statistics, and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.alien_shot_timer = 0
        self.ship_invulnerability_timer = 0

        self._create_fleet()

        #start Alien Invasion in an active state.
        self.game_active = False 

        #make the play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game"""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()
                self.explosions.update()

                self.ship_invulnerability_timer -= self.clock.get_time()

                # Increase the alien firing timer. 
                self.alien_shot_timer += self.clock.get_time()

                # Check whether the aliens should fire.
                self._check_alien_shooting()
            
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type ==pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            #reset the game settings.
            self.settings.initialize_dynamic_settings()
            self.game_active = True 

            #get rid of any remaining bullets and liens.
            self.bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()
            self.alien_shot_timer = 0

            #create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            #reset the game statistics
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()

            #hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _fire_alien_bullet(self, alien):
        """Fire a bullet from an alien."""
        new_bullet = AlienBullet(self, alien)
        self.alien_bullets.add(new_bullet)

    def _check_alien_shooting(self):
        """Fire bullets from the bottom alien in each column."""
        if self.alien_shot_timer >= self.settings.alien_shot_interval:
            bottom_aliens = self._get_bottom_aliens()

            for alien in bottom_aliens:
                self._fire_alien_bullet(alien)

            self.alien_shot_timer = 0

    def _get_bottom_aliens(self):
        """Find the bottom alien in each column."""
        bottom_aliens = {}

        for alien in self.aliens.sprites():
            column_x = alien.rect.centerx

            if column_x not in bottom_aliens:
                bottom_aliens[column_x] = alien
            elif alien.rect.y > bottom_aliens[column_x].rect.y:
                bottom_aliens[column_x] = alien

        return list(bottom_aliens.values())

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        #update bullet positions.
        self.bullets.update()

        #get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _update_alien_bullets(self): 
        """Update the alien bullets and remove bullets off screen."""
        self.alien_bullets.update()

        for bullet in self.alien_bullets.copy(): 
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)

        self._check_alien_bullet_collisions()

    def _check_alien_bullet_collisions(self):
        """Check for collisions between alien bullets and the ship."""
        for bullet in self.alien_bullets.copy():
            if (bullet.rect.colliderect(self.ship.rect)
                    and self.ship_invulnerability_timer <= 0):
                self.alien_bullets.remove(bullet)
                self._ship_hit()
                break

    def _check_bullet_alien_collisions(self):
        """respond to bullet-alien collisions."""
        #remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                for alien in aliens:
                    explosion = Explosion(self, alien)
                    self.explosions.add(explosion)

                self.stats.score += self.settings.alien_points * len(aliens)
                self.stats.aliens_destroyed += len(aliens)

            self.sb.prep_score()

        if not self.aliens:
            #destroy exisitng bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        self.stats.ship_health -= 10
        self.ship_invulnerability_timer = self.settings.ship_invulnerability_time

        # Check whether the ship has been destroyed.
        if self.stats.ship_health <= 0:
            self.game_active = False
            self.aliens.empty()
            self.alien_bullets.empty()

            # Add the final score to the top 3.
            self.sb.update_high_scores()

            pygame.mouse.set_visible(True)
            return

        # Get rid of any remaining bullets.
        self.bullets.empty()
        self.alien_bullets.empty()
        self.alien_shot_timer = 0

        # Center the ship.
        self.ship.center_ship()

        # Pause briefly.
        sleep(0.5)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        #look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        #create an alien and keep adding aliens until there's no room left.
        #spacing between aliens is one alien width and one alien height
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, 100
        while current_y < 400:
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 4 * alien_width 

            #finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height 


    def _create_alien(self, x_position, y_position):
        """create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                #treat this the same as if the ship got hit.
                self._ship_hit()
                break 
    
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        #draw alien ship explosions.
        for explosion in self.explosions:
            explosion.draw()

        #draw the score information.
        self.sb.show_score()

        #draw the health bar information.
        self.sb.show_health_bar()

        #draw the play button if the game is inactive.
        if not self.game_active:
            self.sb.show_game_over()
            self.sb.show_game_over_stats()
            self.play_button.draw_button()
            self.sb.show_high_scores()

        # make the most recently drawn screen visible, i.e. updates the game window.
        pygame.display.flip()


if __name__ == '__main__':
    # make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()