import os
import random
import pygame
from settings import TILE_SIZE, RED
from enum import Enum

class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    IDLE = 0
    def reverse(self):
        return Direction(-self.value)
    def pause(self):
        return Direction(0)
    def __mul__(self, operand):
        if operand == -1:
            return Direction(-self.value)
        raise ValueError("Multiplication only support -1 to reverse direction")


class Action(Enum):
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

    def __init__(self, x, y, direction, inner_radius=50, outer_radius=200, full_damage=100, vel_x=7, vel_y=-11):
        super().__init__()
        self._timer = 100
        self._vel_x = vel_x
        self._vel_y = vel_y
        self._inner_radius = inner_radius
        self._outer_radius = outer_radius
        self._full_damage = full_damage
        self._image = Grenade.grenade_image
        self._rect = self._image.get_rect()
        self._rect.center = (x, y)
        self._direction = direction

    @property
    def timer(self):
        return self._timer

    @property
    def image(self):
        return self._image
    
    @property
    def rect(self):
        return self._rect

    def damage(self, target_rect):
        manhattan_dist = (abs(self._rect.centerx - target_rect.centerx) +
                          abs(self._rect.centery - target_rect.centery))
        if manhattan_dist > self._outer_radius:
            return 0
        elif manhattan_dist < self._inner_radius:
            return self._full_damage
        else:
            # y = A * (1 - x / B)
            A = self._full_damage
            B = self._outer_radius - self._inner_radius
            return int(A * (1 - (manhattan_dist - self._inner_radius) / B))
        
    def update(self):
        self._vel_y += GRAVITY
        dx = self._vel_x * self._direction.value
        dy = self._vel_y
        if self._rect.bottom + dy > 300:
            dy = 300 - self._rect.bottom
            self._vel_x = 0
        screen_width, screen_height = pygame.display.get_window_size()
        if self._rect.left < 0:
            self._direction = Direction.RIGHT
        elif self._rect.right > screen_width:
            self._direction = Direction.LEFT
        self._rect.x += dx
        self._rect.y += dy
        self._timer -= 1



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
        self.grenade_cooldown = 0
        self.shoot_cooldown = 0
        self.max_health = health
        self.health = self.max_health
        self.direction = Direction.RIGHT
        self.vel_y = 0
        self.jump = False
        self.in_air = True # TODO: should start False?
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
        self.update_time = pygame.time.get_ticks()

        # AI specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 450, self.rect.height)
        self.idling = False
        self.idling_counter = 0


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
        #    self.vel_y
        # self.vel_y = min(self.vel_y, 10)
        dy += self.vel_y

        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx
        self.rect.y += dy


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
            self.move(ai_moving_left, ai_moving_right)
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
                
    def shoot(self):
        #if self.ammo > 0 and self.shoot_cooldown == 0:
        if self.type == 'enemy':
            self.shoot_cooldown = 100
        else:
            self.shoot_cooldown = 10
        self.ammo -= 1
        dx = int(self.rect.size[0] * 0.6 * self.direction.value)
        x = self.rect.centerx + dx
        y = self.rect.centery
        return Bullet(x, y, self.direction)


    def throw(self):
        #if self.grenades > 0 and self.grenade_cooldown == 0:
        if self.type == 'enemy':
            self.grenade_cooldown = 200
        else:
            self.grenade_cooldown = 100
        self.grenades -= 1
        dx = int(self.rect.size[0] * 0.2 * self.direction.value)
        #dy = -int(self.rect.size[1] * 0.2)
        x = self.rect.centerx + dx
        y = self.rect.top#self.rect.centery + dy
        return Grenade(x, y, self.direction)


    def death(self):
        self.health = 0
        self.speed = 0
        self.alive = False


    def draw(self, screen):
        img = pygame.transform.flip(self.image, self.flip, False)
        screen.blit(img, self.rect)

    
        