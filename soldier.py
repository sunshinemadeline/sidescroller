import os
import pygame
from enum import Enum

class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    IDLE = 0

class Actions(Enum):
    IDLE = 0
    RUN = 1
    JUMP = 2
    DEATH = 3

GRAVITY = 0.75

def init():
    Bullet.bullet_image = pygame.image.load('img/icons/bullet.png').convert_alpha()
    Grenade.grenade_image = pygame.image.load('img/icons/grenade.png').convert_alpha()
    Explosion.image_frames = []
    num_of_frames = len(os.listdir(f'img/explosion'))
    for i in range(num_of_frames):
        img = pygame.image.load(f'img/explosion/exp{i}.png').convert_alpha()
        Explosion.image_frames.append(img)
    ItemBox.item_images = {
        'health': pygame.image.load(f'img/icons/health_box.png').convert_alpha(),
        'ammo': pygame.image.load(f'img/icons/ammo_box.png').convert_alpha(),
        'grenade': pygame.image.load(f'img/icons/grenade_box.png').convert_alpha()
    }



class ItemBox(pygame.sprite.Sprite):
    item_images = None

    def __init__(self, x, y, type='ammo'):
        super().__init__()
        self.type = type
        self.image = ItemBox.item_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y - self.image.get_height()) # Russ uses TILE_SIZE

    def update(self):
        pass



class Bullet(pygame.sprite.Sprite):
    bullet_image = None

    def __init__(self, x, y, direction, damage=25, speed=15):
        super().__init__()
        self.image = Bullet.bullet_image
        self.speed = speed
        self.damage = damage
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += self.speed * self.direction.value
        screen_width, screen_height = pygame.display.get_window_size()
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()



class Grenade(pygame.sprite.Sprite):
    grenade_image = None

    def __init__(self, x, y, direction, radius=100, damage=50, vel_x=7, vel_y=-11):
        super().__init__()
        self.timer = 100
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.radius = radius
        self.damage = damage
        self.image = Grenade.grenade_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.vel_x * self.direction.value
        dy = self.vel_y
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.vel_x = 0
        screen_width, screen_height = pygame.display.get_window_size()
        if self.rect.left < 0:
            self.direction = Direction.RIGHT
        elif self.rect.right > screen_width:
            self.direction = Direction.LEFT
        self.rect.x += dx
        self.rect.y += dy
        self.timer -= 1



class Explosion(pygame.sprite.Sprite):
    image_frames = None

    def __init__(self, x, y, scale=1):
        super().__init__()
        self.frames = []
        self.frame_idx = 0
        for img in Explosion.image_frames:
            new_width = int(img.get_width() * scale)
            new_height = int(img.get_height() * scale)
            img = pygame.transform.scale(img, (new_width, new_height))
            self.frames.append(img)
        self.image = self.frames[self.frame_idx]
        self.rect = self.frames[self.frame_idx].get_rect()
        self.rect.center = (x, y)
        self.counter = 0

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
            
            


class Soldier(pygame.sprite.Sprite):
    def __init__(self, x, y, type='player', scale=2, speed=5, health=100, ammo=20, grenades=5):
        super().__init__()
        self.alive = True
        self.type = type
        self.scale = scale
        self.speed = speed
        self.start_ammo = ammo
        self.ammo = self.start_ammo
        self.start_grenades = grenades
        self.grenades = self.start_grenades
        self.shoot_cooldown = 0
        self.max_health = health
        self.health = self.max_health
        self.direction = Direction.RIGHT
        self.vel_y = 0
        self.jump = False
        self.in_air = True # TODO: should start False?
        self.flip = False
        self.frame_list = []
        self.frame_idx = 0
        self.action = Actions.IDLE
        action_list = ['Idle', 'Run', 'Jump', 'Death']
        for action in action_list:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/{self.type}/{action}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.type}/{action}/{i}.png')
                img = img.convert_alpha()
                new_width = int(img.get_width() * scale)
                new_height = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (new_width, new_height))
                temp_list.append(img)
            self.frame_list.append(temp_list)
        self.image = self.frame_list[self.action.value][self.frame_idx]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.update_time = pygame.time.get_ticks()

    def update(self, new_action=None):
        ANIMATION_COOLDOWN = 100
        if new_action is not None and new_action != self.action:
            self.action = new_action
            self.frame_idx = 0
            self.update_time = pygame.time.get_ticks()
        self.image = self.frame_list[self.action.value][self.frame_idx]
        if pygame.time.get_ticks() > self.update_time + ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_idx += 1
        if self.frame_idx >= len(self.frame_list[self.action.value]):
            if self.action == Actions.DEATH:
                self.frame_idx = len(self.frame_list[self.action.value]) - 1
            else:
                self.frame_idx = 0
        # shooting timer
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = Direction.LEFT
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = Direction.RIGHT

        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        #if self.vel_y > 10:
        #    self.vel_y = min(self.vel_y, 10)
        dy += self.vel_y

        # TODO: fix with real floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy

    def shoot(self, bullet_sprite_group):
        if self.ammo > 0 and self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            self.ammo -= 1
            dx = int(self.rect.size[0] * 0.6 * self.direction.value)
            x = self.rect.centerx + dx
            y = self.rect.centery
            bullet_sprite_group.add(Bullet(x, y, self.direction))

    def throw(self, grenade_sprite_group):
        if self.grenades > 0:
            self.grenades -= 1
            dx = int(self.rect.size[0] * 0.2 * self.direction.value)
            #dy = -int(self.rect.size[1] * 0.2)
            x = self.rect.centerx + dx
            y = self.rect.top#self.rect.centery + dy
            grenade_sprite_group.add(Grenade(x, y, self.direction))


    def death(self):
        self.health = 0
        self.speed = 0
        self.alive = False
        #self.kill()

    def draw(self, screen):
        img = pygame.transform.flip(self.image, self.flip, False)
        screen.blit(img, self.rect)

    
        