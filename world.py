
import csv
import pygame
from soldier import Player, Enemy
from weapons import ItemBox                                       # type: ignore
from settings import WHITE, RED, GREEN   
from settings import ROWS, COLS, TILE_SIZE, TILE_TYPES            # type: ignore
from settings import GRAVITY, Direction

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


class World():
    def __init__(self):
        self._tile_img_list = []
        self._player = None
        self._health_bar = None
        self._obstacle_group = pygame.sprite.Group()
        self._water_group = pygame.sprite.Group()
        self._decoration_group = pygame.sprite.Group()
        self._exit_group = pygame.sprite.Group()
        self._item_group = pygame.sprite.Group()
        self._enemy_group = pygame.sprite.Group()
        self._bullet_group = pygame.sprite.Group()
        self._grenade_group = pygame.sprite.Group()
        self._explosion_group = pygame.sprite.Group()

        for tile_num in range(TILE_TYPES):
            img = pygame.image.load(f'img/tile/{tile_num}.png')
            img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self._tile_img_list.append(img)

    @property
    def player(self):
        return self._player
    
    @property
    def health_bar(self):
        return self._health_bar

    @property
    def item_group(self):
        return self._item_group
    
    @property
    def enemy_group(self):
        return self._enemy_group
    
    @property
    def bullet_group(self):
        return self._bullet_group

    @property
    def grenade_group(self):
        return self._grenade_group

    @property
    def explosion_group(self):
        return self._explosion_group

    @property
    def obstacles(self):
        return self._obstacle_group
    
    @property
    def decoration_group(self):
        return self._decoration_group
    
    @property
    def obstacle_group(self):
        return self._obstacle_group

    @property
    def water_group(self):
        return self._water_group

    @property
    def exit_group(self):
        return self._exit_group

    def load_game_level(self, level):
        # Create tile list for this level
        world_data = []
        for row in range(ROWS):
            empty_row = [-1] * COLS
            world_data.append(empty_row)

        with open(f'level{level}_data.csv', 'r') as csvfile:  # Russ: newline=''
            reader = csv.reader(csvfile, delimiter=',')
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    world_data[y][x] = int(tile)

        # Note: -1 is an empty space
        # TODO: Combine with previous code
        for y, row in enumerate(world_data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = self._tile_img_list[tile]
                    rect = img.get_rect()
                    rect.x = x * TILE_SIZE
                    rect.y = y * TILE_SIZE
                    #tile_data = (img, rect)

                    if tile < 9: # TODO: 9 is a magic number because 0-8 are dirt tiles
                        obstacle_tile = Obstacle(img, rect.x, rect.y)
                        self._obstacle_group.add(obstacle_tile)
                    elif tile < 11:
                        water_tile = Water(img, rect.x, rect.y)
                        self._water_group.add(water_tile)
                    elif tile < 15:
                        decoration_tile = Decoration(img, rect.x, rect.y)
                        self._decoration_group.add(decoration_tile)
                    elif tile == 15:
                        self._player = Player(rect.x, rect.y, 'player', 1.65)
                        self._health_bar = HealthBar(10, 10, self._player.health, self._player.max_health)
                        print(f"Player 1 loaded at location ({x},{y})")
                    elif tile == 16:
                        enemy = Enemy(rect.x, rect.y, 'enemy', 1.65, 2)
                        self._enemy_group.add(enemy)
                        print(f"Enemy loaded at location ({x},{y})")
                    elif tile == 17:
                        item = ItemBox(rect.x, rect.y, 'ammo')
                        self._item_group.add(item)
                        print(f"Ammo box loaded at location ({x},{y})")
                    elif tile == 18:
                        item = ItemBox(rect.x, rect.y, 'grenade')
                        self._item_group.add(item)
                        print(f"Grenade box loaded at location ({x},{y})")
                    elif tile == 19:
                        item = ItemBox(rect.x, rect.y, 'health')
                        self._item_group.add(item)
                        print(f"Health box loaded at location ({x},{y})")
                    elif tile == 20: # level exit
                        exit_tile = Exit(img, rect.x, rect.y)
                        self._exit_group.add(exit_tile)
        return
    
    def update_physics(self):
        self.update_physics_sprite(self.player)
        for enemy in self.enemy_group:
            self.update_physics_sprite(enemy)
        for grenade in self.grenade_group:
            self.update_physics_sprite(grenade)

    def update_physics_sprite(self, sprite):
        '''
        Calculates and moves a sprite's position based on its current velocity
        and the effect of gravity.
        '''

        # Calculate vertical movement
        sprite.vel_y += GRAVITY
        sprite.vel_y = min(10, sprite.vel_y)
        dy = sprite.vel_y

        # Calculate lateral movement
        dx = sprite.vel_x * sprite.direction.value

        for tile in self._obstacle_group:

            # Handle collisions in x-direction
            predicted_x = pygame.Rect(sprite.rect.x + dx, sprite.rect.y, 
                                      sprite.rect.width, sprite.rect.height)
            if tile.rect.colliderect(predicted_x):
                if sprite.direction == Direction.LEFT:
                    pass
                    #sprite.rect.left = tile.rect.right
                    #limit_value = tile.rect.right - sprite.rect.left
                    #dx = min(dx, limit_value)
                elif sprite.direction == Direction.RIGHT:
                    pass
                    #sprite.rect.right = tile.rect.left
                    #limit_value = tile.rect.left - sprite.rect.right
                    #dx = max(dx, limit_value)
                #dx = 0

            # Handle collisions in y-direction
            predicted_y = pygame.Rect(sprite.rect.x, sprite.rect.y + dy, 
                                      sprite.rect.width, sprite.rect.height)
            if tile.rect.colliderect(predicted_y):
                # Jumping up and hitting head on bottom of terrain
                #if sprite.vel_y < 0:
                #    sprite.vel_y = 0
                #    dy = tile[1].bottom - sprite.rect.top
                #    dy = 0
                # Falling down and resting on top of terrain 
                if sprite.vel_y >= 0:
                    sprite.landed(sprite.vel_y)
                    #sprite.vel_y = 0
                    #sprite.in_air = False
                    limit_value = tile.rect.top - sprite.rect.bottom
                    dy = min(dy, limit_value)

        # Move the sprite
        sprite.rect.x += dx
        sprite.rect.y += dy

    def draw(self, screen):
        self._obstacle_group.draw(screen)
        self._water_group.draw(screen)
        self._exit_group.draw(screen)        
        self._decoration_group.draw(screen)
        self._item_group.draw(screen)
        self._bullet_group.draw(screen)
        self._grenade_group.draw(screen)
        self._explosion_group.draw(screen)
        #self._enemy_group.draw(screen)
        for enemy in self._enemy_group:
            enemy.draw(screen)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass