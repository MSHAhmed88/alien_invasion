import sys
import random
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
from power_up import PowerUp
from boss import Boss
from boss_bullet import BossBullet

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
        self.bosses = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.boss_shot_timer = 0
        self.explosions = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.alien_shot_timer = 0
        self.ship_invulnerability_timer = 0
        self.firing = False
        self.rapid_fire_shot_timer = 0

        self._create_fleet()

        #start Alien Invasion in an active state.
        self.game_active = False
        self.game_started = False

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
                self.bosses.update()
                self._update_boss_bullets()
                self._check_boss_bullet_collisions()

                if self.bosses:
                    self.boss_shot_timer += self.clock.get_time()

                    if self.boss_shot_timer >= 1000:
                        for boss in self.bosses:
                            self._fire_boss_bullet(boss)

                        self.boss_shot_timer = 0

                self._update_alien_bullets()
                self._check_power_up_collisions()
                self.explosions.update()
                self.power_ups.update()

                self.ship_invulnerability_timer -= self.clock.get_time()
                self.stats.rapid_fire_timer -= self.clock.get_time() / 1000
                self.stats.shield_timer -= self.clock.get_time() / 1000

                if self.firing and self.stats.rapid_fire_timer > 0:
                    self.rapid_fire_shot_timer -= self.clock.get_time()

                    if self.rapid_fire_shot_timer <= 0:
                        self._fire_bullet()
                        self.rapid_fire_shot_timer = self.settings.rapid_fire_interval

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
            self.game_started = True

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
            self.firing = True
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_SPACE:
            self.firing = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _fire_alien_bullet(self, alien):
        """Fire a bullet from an alien."""
        new_bullet = AlienBullet(self, alien)
        self.alien_bullets.add(new_bullet)

    def _fire_boss_bullet(self, boss):
        """Fire a bullet from the boss."""
        new_bullet = BossBullet(self, boss)
        self.boss_bullets.add(new_bullet)

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

    def _update_boss_bullets(self):
        """Update the boss bullets and remove bullets off screen."""
        self.boss_bullets.update()

        for bullet in self.boss_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.boss_bullets.remove(bullet)

    def _check_alien_bullet_collisions(self):
        """Check for collisions between alien bullets and the ship."""
        for bullet in self.alien_bullets.copy():
            if (bullet.rect.colliderect(self.ship.rect)
                    and self.ship_invulnerability_timer <= 0
                    and self.stats.shield_timer <= 0):
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
                    self._maybe_drop_power_up(alien)

                self.stats.score += self.settings.alien_points * len(aliens)
                self.stats.aliens_destroyed += len(aliens)

            self.sb.prep_score()

        if not self.aliens and not self.bosses:
            # Destroy existing bullets.
            self.bullets.empty()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

            # Create the boss at the boss level.
            if self.stats.level == self.settings.boss_level:
                self._create_boss()
            else:
                self._create_fleet()
                self.settings.increase_speed()

        # Check for collisions between bullets and the boss.
        for bullet in self.bullets.copy():
            boss_collisions = pygame.sprite.spritecollide(
                bullet,
                self.bosses,
                False
            )

            if boss_collisions:
                bullet.kill()

                for boss in boss_collisions:
                    boss.health -= 1

                    if boss.health <= 0:
                        explosion = Explosion(self, boss, size=160)
                        self.explosions.add(explosion)

                        boss.kill()

    def _check_boss_bullet_collisions(self):
        """Check for collisions between boss bullets and the ship."""

        for bullet in self.boss_bullets.copy():

            if (bullet.rect.colliderect(self.ship.rect)
                    and self.ship_invulnerability_timer <= 0
                    and self.stats.shield_timer <= 0):

                self.boss_bullets.remove(bullet)
                self._ship_hit(damage=20)
                break

    def _ship_hit(self, damage=10):
        """Respond to the ship being hit."""
        self.stats.ship_health -= damage
        self.ship_invulnerability_timer = self.settings.ship_invulnerability_time

        # Check whether the ship has been destroyed.
        if self.stats.ship_health <= 0:
            self.game_active = False
            self.aliens.empty()
            self.alien_bullets.empty()
            self.bosses.empty()
            self.boss_bullets.empty()

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

    def _check_power_up_collisions(self):
        """Check for collisions between power-ups and the ship."""
        collisions = pygame.sprite.spritecollide(
            self.ship,
            self.power_ups,
            True
        )

        for power_up in collisions:
            if power_up.power_up_type == "health":
                self.stats.ship_health += 10

                if self.stats.ship_health > self.settings.ship_health:
                    self.stats.ship_health = self.settings.ship_health

            elif power_up.power_up_type == "rapid_fire":
                self.stats.rapid_fire_timer = self.settings.rapid_fire_duration
                self.rapid_fire_shot_timer = 0

            elif power_up.power_up_type == "shield":
                self.stats.shield_timer = self.settings.shield_duration

    def _maybe_drop_power_up(self, alien):
        """Randomly create a power-up when an alien is destroyed."""
        if random.random() < self.settings.power_up_drop_chance:

            if self.stats.ship_health < self.settings.ship_health:
                power_up_type = random.choices(
                    ["health", "rapid_fire", "shield"],
                    weights=[75, 15, 10],
                    k=1
                )[0]
            else:
                power_up_type = random.choices(
                    ["rapid_fire", "shield"],
                    weights=[60, 40],
                    k=1
                )[0]

            power_up = PowerUp(self, power_up_type)
            power_up.rect.center = alien.rect.center
            power_up.y = float(power_up.rect.y)
            self.power_ups.add(power_up)

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
        for boss in self.bosses:
            self.screen.blit(boss.image, boss.rect)
            boss.draw_health_bar()
        for bullet in self.boss_bullets:
            bullet.draw_bullet()

        #draw alien ship explosions.
        for explosion in self.explosions:
            explosion.draw()

        #draw power ups.
        for power_up in self.power_ups:
            power_up.draw()

        #draw the score information.
        self.sb.show_score()

        #draw the health bar information.
        self.sb.show_health_bar()

        #draw the play button if the game is inactive.
        if not self.game_active and self.game_started:
            self.sb.show_game_over_box()
            self.sb.show_high_scores_title()
            self.sb.show_high_scores()
            self.sb.show_game_over()
            self.sb.show_game_over_stats()

        # Draw the Play button when the game is inactive.
        if not self.game_active:
            self.play_button.draw_button()

        # make the most recently drawn screen visible, i.e. updates the game window.
        pygame.display.flip()


    def _create_boss(self):
        """Create the boss."""
        boss = Boss(self)
        self.bosses.add(boss)


if __name__ == '__main__':
    # make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()