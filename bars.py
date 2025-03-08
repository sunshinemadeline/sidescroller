import pygame
from settings import WHITE, RED, GREEN                              # type: ignore

class HealthBar():
    def __init__(self, x, y, cur_health, max_health, width=150, height=20):
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.cur_health = cur_health
        self.max_health = max_health
    def draw(self, screen, health_value):
        self.cur_health = health_value
        health_size = self.width * self.cur_health / self.max_health
        pygame.draw.rect(screen, WHITE, (self.x-1, self.y-1, self.width+2, self.height+2))
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, health_size, self.height))

