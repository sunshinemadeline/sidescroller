import os
import random
import pygame
from weapons import Bullet, Grenade                               # type: ignore
from settings import Direction, Action
from settings import TILE_SIZE, WHITE, RED, GREEN


# All soldiers share these common animation types
animation_types = ['Idle', 'Run', 'Jump', 'Death']


class HealthBar():
    '''
    Graphic to visualize the player's health as a green/red rectangle.
    '''

    def __init__(self, x, y, max_health, width=150, height=20):
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.cur_health = max_health
        self.max_health = max_health

    def draw(self, screen, health_value):
        self.cur_health = health_value
        health_size = self.width * self.cur_health / self.max_health
        pygame.draw.rect(screen, WHITE, (self.x-1, self.y-1, self.width+2, self.height+2))
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, health_size, self.height))


def init():
    ''' Initializes the soldier module by preloading all images from disk. '''

    # Images for player animation
    Player.animation_images = []
    for action in animation_types:
        image_list = []
        frame_count = len(os.listdir(f'img/player/{action}'))
        for i in range(frame_count):
            img = pygame.image.load(f'img/player/{action}/{i}.png')
            img = img.convert_alpha()
            image_list.append(img)
        Player.animation_images.append(image_list)

    # Images for enemy animation
    Enemy.animation_images = []
    for action in animation_types:
        image_list = []
        frame_count = len(os.listdir(f'img/enemy/{action}'))
        for i in range(frame_count):
            img = pygame.image.load(f'img/enemy/{action}/{i}.png')
            img = img.convert_alpha()
            image_list.append(img)
        Enemy.animation_images.append(image_list)

        

class Soldier(pygame.sprite.Sprite):
    def __init__(self, x, y, type='player', scale=2, speed=5, health=100, ammo=20, grenades=5):
        super().__init__()
        self.alive = True
        self.type = type
        self.scale = scale
        self.speed = speed
        self.start_ammo = ammo
        self.ammo = self.start_ammo
        self.max_ammo = self.start_ammo * 2
        self.start_grenades = grenades
        self.grenades = self.start_grenades
        self.max_grenades = self.start_grenades * 2
        self.grenade_cooldown = 0
        self.shoot_cooldown = 0
        self.max_health = health
        self.health = self.max_health
        self.direction = Direction.RIGHT
        self.vel_y = 0
        self.vel_x = 0
        self.in_air = True # TODO: should start False?
        self.jump = False
        self.flip = False

        # Action/Animation sprite related variables
        self.action = Action.IDLE
        self.frame_idx = 0
        self.animation_list = []
        for action in ['Idle', 'Run', 'Jump', 'Death']:
            frame_list = []
            frame_count = len(os.listdir(f'img/{self.type}/{action}'))
            for i in range(frame_count):
                img = pygame.image.load(f'img/{self.type}/{action}/{i}.png')
                img = img.convert_alpha()
                new_width = int(img.get_width() * scale)
                new_height = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (new_width, new_height))
                frame_list.append(img)
            self.animation_list.append(frame_list)
        self.image = self.animation_list[self.action.value][self.frame_idx]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        #self.width = self.image.get_width()
        #self.height = self.image.get_height()
        self.update_time = pygame.time.get_ticks()

    def update(self, new_action=None):
        ANIMATION_COOLDOWN = 100
        
        if new_action is not None and new_action != self.action:
            self.action = new_action
            self.frame_idx = 0
            self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.action.value][self.frame_idx]

        if pygame.time.get_ticks() > self.update_time + ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_idx += 1
        if self.frame_idx >= len(self.animation_list[self.action.value]):
            if self.action == Action.DEATH:
                self.frame_idx = len(self.animation_list[self.action.value]) - 1
            else:
                self.frame_idx = 0
        
        # cooldown timers
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.grenade_cooldown > 0:
            self.grenade_cooldown -= 1

    def move(self, moving_left, moving_right, jump):

        # Handle vertical movement
        if jump == True and self.in_air == False:
            self.vel_y = -11
            self.in_air = True

        # Handle lateral movement
        if moving_left and not moving_right:
            self.vel_x = self.speed
            self.flip = True
            self.direction = Direction.LEFT
        elif moving_right and not moving_left:
            self.vel_x = self.speed
            self.flip = False
            self.direction = Direction.RIGHT
        else:
            self.vel_x = 0

    def landed(self, impact_velocity):
        self.vel_y = 0
        self.in_air = False

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            dx = int(self.rect.size[0] * 0.6 * self.direction.value)
            x = self.rect.centerx + dx
            y = self.rect.centery
            return Bullet(x, y, self.direction)
        else:
            return None

    def throw(self):
        if self.grenades > 0:
            self.grenades -= 1
            dx = int(self.rect.size[0] * 0.2 * self.direction.value)
            #dy = -int(self.rect.size[1] * 0.2)
            x = self.rect.centerx + dx
            y = self.rect.top#self.rect.centery + dy
            return Grenade(x, y, self.direction)
        else:
            return None

    def death(self):
        self.update(Action.DEATH)
        self.health = 0
        self.speed = 0
        self.vel_x = 0
        self.alive = False

    def draw(self, screen, screen_scroll):
        img = pygame.transform.flip(self.image, self.flip, False)
        self.rect.x += screen_scroll
        screen.blit(img, self.rect)

    

class Enemy(Soldier):
    animation_images = None

    def __init__(self, x, y, type='player', scale=2, speed=5, health=100, ammo=20, grenades=5):
        super().__init__(x, y, type, scale, speed, health, ammo, grenades)
        
        # AI related variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 450, self.rect.height)
        self.idling = False
        self.idling_counter = 0

        # Animation related variables
        self.animation_list = []
        for action in animation_types:
            frame_list = []
            frame_count = len(os.listdir(f'img/{self.type}/{action}'))
            for i in range(frame_count):
                img = pygame.image.load(f'img/{self.type}/{action}/{i}.png')
                img = img.convert_alpha()
                new_width = int(img.get_width() * scale)
                new_height = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (new_width, new_height))
                frame_list.append(img)
            self.animation_list.append(frame_list)

    def shoot(self):
        self.shoot_cooldown = 100
        return super().shoot()

    def throw(self):
        self.grenade_cooldown = 200
        return super().throw()

    # TODO: This is only for computer soldiers, use inheritence
    def ai_shoot(self):
        self.update(Action.IDLE)
        self.idling = True
        self.idling_counter = random.randint(20, 40)
        return self.shoot()
    

    # TODO: This is only for computer soldiers, use inheritence
    def ai_move(self):
        if self.idling == False and random.randint(1, 1000) < 5:
            self.update(Action.IDLE)
            self.idling = True
            self.idling_counter = random.randint(20, 40)

        # handle idling
        if self.idling:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idling = False
        
        # handle movement
        else:
            if self.direction == Direction.RIGHT:
                ai_moving_right = True
                ai_moving_left = False
            else:
                ai_moving_right = False
                ai_moving_left = True
            self.move(ai_moving_left, ai_moving_right, False)
            self.update(Action.RUN)
            self.move_counter += 1

            # Update AI vision as the enemy moves
            dx = self.vision.width // 2 * self.direction.value
            self.vision.center = (self.rect.centerx + dx, self.rect.centery)
            #pygame.draw.rect(screen, RED, self.vision)

            if self.move_counter > TILE_SIZE:
                self.direction *= -1
                self.move_counter *= -1
        
        return None


class Player(Soldier):
    animation_images = None
    
    def __init__(self, x, y, type='player', scale=2, speed=5, health=100, ammo=20, grenades=5):
        super().__init__(x, y, type, scale, speed, health, ammo, grenades)

        # Animation related variables
        self.animation_list = []
        for action in animation_types:
            frame_list = []
            frame_count = len(os.listdir(f'img/{self.type}/{action}'))
            for i in range(frame_count):
                img = pygame.image.load(f'img/{self.type}/{action}/{i}.png')
                img = img.convert_alpha()
                new_width = int(img.get_width() * scale)
                new_height = int(img.get_height() * scale)
                img = pygame.transform.scale(img, (new_width, new_height))
                frame_list.append(img)
            self.animation_list.append(frame_list)

    def shoot(self):
        self.shoot_cooldown = 10
        return super().shoot()

    def throw(self):
        self.grenade_cooldown = 100
        return super().throw()
