import pygame 

_LEFT_BUTTON = 0
_MIDDLE_BUTTON = 1
_RIGHT_BUTTON = 2

class Button():
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