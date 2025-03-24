
import pygame
from pygame.image import load as load
from os import listdir


class ItemBox(pygame.sprite.Sprite):
    ''' Supplies for the player to collect with ammo, grenades, or health. '''

    images = {
        'ammo': load(f'img/icons/ammo_box.png').convert_alpha(),
        'health': load(f'img/icons/health_box.png').convert_alpha(),
        'grenade': load(f'img/icons/grenade_box.png').convert_alpha(),
    }

    def __init__(self, x, y, box_type='ammo', quantity=20):
        super().__init__()
        self.box_type = box_type
        self.quantity = quantity
        self.image = ItemBox.images[box_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y - self.image.get_height())
        
    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        screen.blit(self.image, (self.rect.x + screen_scroll, self.rect.y))



class Bullet(pygame.sprite.Sprite):
    ''' Ammunition for the soldiers to shoot. '''
    image = pygame.image.load('img/icons/bullet.png').convert_alpha()
    sound_fx = pygame.mixer.Sound('audio/shot.wav')
    sound_fx.set_volume(0.4)

    def __init__(self, x, y, direction, damage=25, speed=15):
        super().__init__()
        self.speed = speed
        self.damage = damage
        self.direction = direction
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        Bullet.sound_fx.play()

    def update(self):
        self.rect.x += self.speed * self.direction.value

    def draw(self, screen, screen_scroll):
        screen.blit(self.image, (self.rect.x + screen_scroll, self.rect.y))



class Grenade(pygame.sprite.Sprite):

    image = pygame.image.load('img/icons/grenade.png').convert_alpha()

    def __init__(self, x, y, direction, inner_radius=50, outer_radius=200, full_damage=100, vel_x=7, vel_y=-11):
        super().__init__()
        self.fuse_timer = 100
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.in_air = True
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.full_damage = full_damage
        self.image = Grenade.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def damage_at(self, pos_rect):
        manhattan_dist = (abs(self.rect.centerx - pos_rect.centerx) +
                          abs(self.rect.centery - pos_rect.centery))
        if manhattan_dist > self.outer_radius:
            return 0
        elif manhattan_dist < self.inner_radius:
            return self.full_damage
        else:
            # y = A * (1 - x / B)
            A = self.full_damage
            B = self.outer_radius - self.inner_radius
            return int(A * (1 - (manhattan_dist - self.inner_radius) / B))
    
    def landed(self, impact_velocity):
        self.vel_y = 0
        self.vel_x = 0
        self.in_air = False

    def update(self):
        self.fuse_timer -= 1

    def draw(self, screen, screen_scroll):
        screen.blit(self.image, (self.rect.x + screen_scroll, self.rect.y))


class Explosion(pygame.sprite.Sprite):
    ''' Animation sequence object for an exploding grenade. '''

    animation_list = []
    num_of_frames = len(listdir(f'img/explosion'))
    for i in range(num_of_frames):
        img = pygame.image.load(f'img/explosion/exp{i}.png').convert_alpha()
        animation_list.append(img)
    sound_fx = pygame.mixer.Sound('audio/grenade.wav')
    sound_fx.set_volume(1)

    def __init__(self, x, y, scale=1):
        super().__init__()
        self.frames = []
        self.frame_idx = 0
        self.counter = 0
        num_of_frames = len(Explosion.animation_list)
        for i in range(num_of_frames):
            img = Explosion.animation_list[i]             # TODO: try to move into class variable
            new_width = int(img.get_width() * scale)
            new_height = int(img.get_height() * scale)
            img = pygame.transform.scale(img, (new_width, new_height))
            self.frames.append(img)
        self.image = self.frames[self.frame_idx]
        self.rect = self.frames[self.frame_idx].get_rect()
        self.rect.center = (x, y)
        Explosion.sound_fx.play()

    def update(self):
        ANIMATION_COOLDOWN = 4
        self.counter += 1
        if self.counter > ANIMATION_COOLDOWN:
            self.counter = 0
            self.frame_idx += 1
            if self.frame_idx >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_idx]

    def draw(self, screen, screen_scroll):
        screen.blit(self.image, (self.rect.x + screen_scroll, self.rect.y))

