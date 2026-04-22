import pygame
from clock import MickeyClock

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey's Clock")

clock = pygame.time.Clock()
mickey_clock = MickeyClock(screen)

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mickey_clock.update()
    mickey_clock.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()