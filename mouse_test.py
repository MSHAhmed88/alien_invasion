import pygame
import time

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Mouse Test")

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((230, 230, 230))
    pygame.display.flip()

pygame.quit()
