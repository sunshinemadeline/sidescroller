import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS            # type: ignore
from settings import BG_COLOR, PINK, BLACK                       # type: ignore
from enum import Enum

_LEFT_BUTTON = 0    # TODO: CLean up
_MIDDLE_BUTTON = 1
_RIGHT_BUTTON = 2

# Drawing colors
BG_COLOR = (144, 201, 120)
BLACK = (32, 32, 32)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
PINK = (235, 65, 54)
RED = (255, 0, 0)

class GameButton():
    def __init__(self, image, x, y, scale=1.0):
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
	
    def is_clicked(self):
        """Returns True if the button is clicked."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()
        if self.rect.collidepoint(mouse_pos):
            if mouse_clicked[_LEFT_BUTTON] and not self.clicked:
                self.clicked = True
                return True
        else:
            self.clicked = False
        return False
    
    def reset(self):
        self.clicked = False


class FadeType(Enum):
    INTRO_EVENT = 0
    LEVEL_EVENT = 1
    DEATH_EVENT = 2


class GameFade():
    def __init__(self, fade_type, color, speed=5):
        '''
        direction = 1 is whole screen
        direction = 2 is vertical
        '''
        self.fade_type = fade_type
        self.color = color
        self.speed = speed
        self.counter = 0
        self.started = False
        self.finished = True

    def begin_fade(self):
        self.counter = 0
        self.started = True
        self.finished = False

    def draw_fade(self, screen):
        # Three types of fades
        if self.fade_type == FadeType.INTRO_EVENT:
            #if self.counter <= SCREEN_WIDTH:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0 - self.counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        elif self.fade_type == FadeType.LEVEL_EVENT:
            #if self.counter <= SCREEN_WIDTH:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0, 0, self.counter, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH - self.counter, 0, SCREEN_WIDTH // 2 - self.counter, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT - self.counter, SCREEN_WIDTH, self.counter))

        elif self.fade_type == FadeType.DEATH_EVENT:
            #if self.counter <= SCREEN_HEIGHT:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, self.counter))
        
        if self.counter >= SCREEN_WIDTH:
            self.finished = True
            self.started = False

