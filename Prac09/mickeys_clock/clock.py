import pygame
import math
import datetime

class MickeyClock:
    def __init__(self, screen):
        self.screen = screen
        self.center = (300, 250)

        self.clock_img = pygame.image.load("images/clock.png")
        self.minute_hand = pygame.image.load("images/min_hand.png")
        self.second_hand = pygame.image.load("images/sec_hand.png")

        self.clock_img = pygame.transform.scale(self.clock_img, (600, 600))

    def get_angle(self):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        minute_angle = -(minutes * 6)
        second_angle = -(seconds * 6)

        return minute_angle, second_angle

    def rotate(self, image, angle):
        rotated = pygame.transform.rotate(image, angle)
        rect = rotated.get_rect(center=self.center)
        return rotated, rect

    def update(self):
        pass

    def draw(self):
        self.screen.blit(self.clock_img, (0, 0))

        minute_angle, second_angle = self.get_angle()

        minute_img, minute_rect = self.rotate(self.minute_hand, minute_angle)
        second_img, second_rect = self.rotate(self.second_hand, second_angle)

        self.screen.blit(minute_img, minute_rect)
        self.screen.blit(second_img, second_rect)