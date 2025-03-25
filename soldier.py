import os
import random
import pygame
from pygame.time import get_ticks
from weapons import Bullet, Grenade
from settings import Direction, Action
from settings import (SOLDIER_SCALE_VALUE, SOLDIER_JUMP_STRENGTH,
                      PLAYER_SHOOT_DELAY, PLAYER_THROW_DELAY,
                      SOLDIER_SHOOT_DELAY, SOLDIER_THROW_DELAY,
                      ANIMATION_DELAY)


# All soldiers share these common animation types
animation_types = ['Idle', 'Run', 'Jump', 'Death']

def generate_animation_frames(base_dirpath):
    '''
    Generates an ordered list of animation frames containing every image in a
    file directory. There are four different animation types and the animation
    sequence for each must be in an appropriately named subdirectory: 'Idle',
    'Run', 'Jump', and 'Death'. The images must be named 1.png, 2.png, 3.png,
    etc. There is no restriction on the number of images in the sequence.
    '''

    animation_images = []
    for action in animation_types:
        image_list = []
        frame_count = len(os.listdir(f'{base_dirpath}/{action}'))
        for i in range(frame_count):
            img = pygame.image.load(f'{base_dirpath}/{action}/{i}.png')
            scaled_width = int(img.get_width() * SOLDIER_SCALE_VALUE)
            scaled_height = int(img.get_height() * SOLDIER_SCALE_VALUE)
            img = img.convert_alpha()
            img = pygame.transform.scale(img, (scaled_width, scaled_height))
            image_list.append(img)
        animation_images.append(image_list)
    return animation_images


class Soldier(pygame.sprite.Sprite):
    '''
    Base class for a soldier object that can be used for all human sprites.
    '''

    # Load media from disk into shared memory for each instance to copy
    jump_fx = pygame.mixer.Sound('audio/jump.wav')
    jump_fx.set_volume(0.5)
    animations = generate_animation_frames('img/enemy')

    def __init__(self, x, y, speed=3, health=100, ammo=20, grenades=5):
        '''
        Initializes a Soldier object by setting all the default values.
        '''        
        super().__init__()
        self.alive = True
        self.health = health
        self.speed = speed
        self.ammo = ammo
        self.grenades = grenades
        self.max_ammo = ammo * 2
        self.max_grenades = grenades * 2
        self.max_health = health
        self.direction = Direction.RIGHT
        self.vel_y = 0
        self.vel_x = 0
        self.in_air = True
        self.jump = False
        self.flip_imgx = False
        self.world_state = None

        # Action/Animation sprite related variables
        self.animations = Soldier.animations
        self.action = Action.IDLE
        self.frame_idx = 0
        self.image = self.animations[self.action][self.frame_idx]
        self.rect = self.image.get_rect()
        self.animation_time = get_ticks()
        self.shoot_time = self.animation_time
        self.throw_time = self.animation_time
        self.shoot_delay = SOLDIER_SHOOT_DELAY
        self.throw_delay = SOLDIER_THROW_DELAY

        # Adjusts the rectangle to be slightly smaller than image so that the
        # player falls through tile gaps; otherwise the player float on air
        self.rect.x += 3
        self.rect.y -= 1
        self.rect.width -= 6
        self.rect.height -= 2
        self.rect.center = (x, y)

    def update(self, world_state, new_action=None):
        '''
        Updates the soldier's internal variables with each iteration through
        the game loop. Mostly used for animation sequences.
        '''

        # The AI will need a view into the world
        self.world_state = world_state
        
        # Update animation type (e.g., Idle -> Run)
        if new_action is not None and new_action != self.action:
            self.animation_time = get_ticks()
            self.action = new_action
            self.frame_idx = 0
        self.image = self.animations[self.action][self.frame_idx]

        # Update timed sequences like animation frames
        if get_ticks() > self.animation_time + ANIMATION_DELAY:
            self.animation_time = get_ticks()
            self.frame_idx += 1
        
        # Animation rollover (except for the death sequence)
        if self.frame_idx >= len(self.animations[self.action]):
            if self.action == Action.DEATH:
                self.frame_idx = len(self.animations[self.action]) - 1
            else:
                self.frame_idx = 0
        
        # Nothing particularly interesting to return
        return None

    def move(self, mleft_cmd, mright_cmd, jump_cmd):
        '''
        Initiates jumping and lateral movements from the Soldier by setting
        initial velocities. It is a response to input from buttons on the
        controller. The physics engine is responsible for tracking/updating
        the position and velocity of the Soldier over time.
        '''

        # Handle vertical movement
        if jump_cmd and not self.in_air:
            Soldier.jump_fx.play()
            self.vel_y = SOLDIER_JUMP_STRENGTH
            self.in_air = True

        # Handle lateral movement
        if mleft_cmd and not mright_cmd:
            self.direction = Direction.LEFT
            self.vel_x = self.speed
            self.flip_imgx = True
        elif mright_cmd and not mleft_cmd:
            self.direction = Direction.RIGHT
            self.vel_x = self.speed
            self.flip_imgx = False
        else:
            # holding both buttons simultaneously
            self.vel_x = 0

    def landed(self, impact_velocity):
        '''
        The physics engine calls this function when the Soldier is jumping and
        hits the ground. It records the fact that the soldier can jump again.
        '''
        self.vel_y = 0
        self.in_air = False

    def shoot(self):
        '''
        Shoots a bullet if the Soldier has one. This function calculates the 
        physical xy-location bullet and its direction of travel. The physics
        engine is responsible for calculating its movements.

        It's important that the bullet starts outside of the Soldier's rect
        or the game engine will detect it as a suicide shot.
        '''

        if (self.ammo > 0 
                and get_ticks() > self.shoot_time + self.shoot_delay):
            self.ammo -= 1
            self.shoot_time = get_ticks()
            x_offset = int(self.rect.size[0] * 0.6 * self.direction.value)
            x = self.rect.centerx + x_offset
            y = self.rect.centery
            return Bullet(x, y, self.direction)
        else:
            return None

    def throw(self):
        '''
        Throws a grenade if the Soldier has one. This function calculates the 
        physical xy-location grenade and its direction of travel. The physics
        engine is responsible for calculating its movements.
        '''
        if (self.grenades > 0 
                and get_ticks() > self.throw_time + self.throw_delay):
            self.grenades -= 1
            self.throw_time = get_ticks()
            x_offset = int(self.rect.size[0] * 0.2 * self.direction.value)
            x = self.rect.centerx + x_offset
            y = self.rect.top
            return Grenade(x, y, self.direction)
        else:
            return None

    def death(self):
        '''
        Kills this Soldier by updating the animation and clearing variables.
        '''
        self.health = 0
        self.vel_x = 0
        self.update(False, Action.DEATH)
        self.alive = False

    def draw(self, screen, camera_x):
        '''
        Draws this Soldier after flipping and setting camera position.
        '''
        img = pygame.transform.flip(self.image, self.flip_imgx, False)
        screen.blit(img, (self.rect.x + camera_x, self.rect.y))

    

class Enemy(Soldier):

    def __init__(self, x, y, speed=3, health=100, ammo=20, grenades=5):
        '''
        Initializes an Enemy object by setting animation frames and delays.
        '''        
        super().__init__(x, y, speed, health, ammo, grenades)
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 450, self.rect.height)
        self.idling = False
        self.idling_counter = 0

    def ai_shoot(self):
        self.update(Action.IDLE)
        self.idling = True
        self.idling_counter = random.randint(20, 40)
        return self.shoot()

    def ai_move(self, movement_counter=50):
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
            #tile_x = self.rect.x // TILE_SIZE
            #tile_y = self.rect.y // TILE_SIZE
            #index_y = len(self.world_view) // 2
            #index_x = len(self.world_view[0]) // 2
            if (self.direction == Direction.RIGHT ):
                    #and self.world_view[index_y][index_x+1] == -1
                    #and self.world_view[index_y+1][index_x+1] != 1):
                ai_moving_right = True
                ai_moving_left = False
            #elif (self.direction == Direction.LEFT 
            #        and self.world_view[index_y][index_x-1] == -1
            #        and self.world_view[index_y+1][index_x-1] != 1):
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

            if self.move_counter > movement_counter:
                self.direction *= -1
                self.move_counter *= -1
        
        return None


class Player(Soldier):
    '''
    This class creates the main character in the game. Usually, this means an
    interactive human player but it's also possible for the character to be
    controlled by a special AI agent.
    '''

    # Player is a different color than the enemies
    animations = generate_animation_frames('img/player')

    def __init__(self, x, y, speed=5, health=100, ammo=20, grenades=5):
        '''
        Initializes a Player object by setting animation frames and delays.
        '''
        super().__init__(x, y, speed, health, ammo, grenades)
        self.animations = Player.animations
        self.shoot_delay = PLAYER_SHOOT_DELAY
        self.throw_delay = PLAYER_THROW_DELAY

