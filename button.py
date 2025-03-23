import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS            # type: ignore
from settings import BG_COLOR, PINK, BLACK                       # type: ignore
from enum import Enum

_LEFT_BUTTON = 0
_MIDDLE_BUTTON = 1
_RIGHT_BUTTON = 2

class GuiButton():
    def __init__(self, image_path, x, y, scale=1.0):
        self.image = pygame.image.load(image_path).convert_alpha()
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)
        self.image = pygame.transform.scale(self.image, (width, height))
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
    STARTLEVEL = 0
    ENDLEVEL = 1
    PLAYERDEATH = 2



class ScreenFade():
    def __init__(self, fade_type, color, speed):
        '''
        direction = 1 is whole screen
        direction = 2 is vertical
        '''
        self.fade_type = fade_type
        self.color = color
        self.speed = speed
        self.counter = 0
        self.finished = True

    def begin_fade(self):
        self.counter = 0
        self.finished = False

    def draw_fade(self, screen):
        # Three types of fades
        if self.fade_type == FadeType.STARTLEVEL:
            #if self.counter <= SCREEN_WIDTH:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0 - self.counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        elif self.fade_type == FadeType.ENDLEVEL:
            #if self.counter <= SCREEN_WIDTH:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0, 0, self.counter, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH - self.counter, 0, SCREEN_WIDTH // 2 - self.counter, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT - self.counter, SCREEN_WIDTH, self.counter))

        elif self.fade_type == FadeType.PLAYERDEATH:
            #if self.counter <= SCREEN_HEIGHT:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, self.counter))
        
        if self.counter >= SCREEN_WIDTH:
            self.finished = True

