
import csv
import pygame
from pygame.sprite import spritecollideany
from soldier import Player, Enemy, HealthBar
from weapons import ItemBox                                       # type: ignore
from settings import (BG_COLOR, WHITE, RED, GREEN,
                      SCREEN_HEIGHT, SCREEN_WIDTH, SCROLL_THRESHOLD,
                      TILE_SIZE, TILE_TYPE_COUNT, ROWS, COLS,
                      DIRT_TILE_LAST, WATER_TILE_LAST, DECORATION_TILE_LAST,
                      PLAYER_TILE_ID, ENEMY_TILE_ID, AMMO_TILE_ID,
                      GRENADE_TILE_ID, HEALTH_TILE_ID, LEVEL_EXIT_TILE_ID,
                      GRAVITY, Direction)


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
        self._current_level = 1

        # Hardcoded background images and layout positions
        self.bg_image_list = [
            pygame.image.load('img/background/sky_cloud.png').convert_alpha(),
            pygame.image.load('img/background/mountain.png').convert_alpha(),
            pygame.image.load('img/background/pine1.png').convert_alpha(),
            pygame.image.load('img/background/pine2.png').convert_alpha()
        ]
        self.bg_image_ypos = [
            0,
            SCREEN_HEIGHT - self.bg_image_list[1].get_height() - 200,
            SCREEN_HEIGHT - self.bg_image_list[2].get_height() - 150,
            SCREEN_HEIGHT - self.bg_image_list[3].get_height()
        ]
        self.bg_width = min([img.get_width() for img in self.bg_image_list])
        self.bg_scroll = 0
        self.screen_scroll = 0

        # Global fonts
        self._font = pygame.font.SysFont('Futura', 30)

        for tile_num in range(TILE_TYPE_COUNT):
            img = pygame.image.load(f'img/tile/{tile_num}.png').convert_alpha()
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
    def decoration_group(self):
        return self._decoration_group

    @property
    def obstacles(self):
        return self._obstacle_group
    
    @property
    def obstacle_group(self):
        return self._obstacle_group

    @property
    def water_group(self):
        return self._water_group

    @property
    def exit_group(self):
        return self._exit_group

    def load_game_tile(self, tile, idx_x, idx_y):
        '''
        Loads an individual game tile by creating the tile object and adding
        it to the appropriate sprite group.
        '''
        img = self._tile_img_list[tile]
        rect = img.get_rect()
        rect.x = idx_x * TILE_SIZE
        rect.y = idx_y * TILE_SIZE

        if tile <= DIRT_TILE_LAST:
            obstacle_tile = Obstacle(img, rect.x, rect.y)
            self._obstacle_group.add(obstacle_tile)
        elif tile <= WATER_TILE_LAST:
            water_tile = Water(img, rect.x, rect.y)
            self._water_group.add(water_tile)
        elif tile <= DECORATION_TILE_LAST:
            decoration_tile = Decoration(img, rect.x, rect.y)
            self._decoration_group.add(decoration_tile)
        elif tile == PLAYER_TILE_ID:
            self._player = Player(rect.x, rect.y, 'player', 1.65)
            self._health_bar = HealthBar(10, 10, self._player.max_health)
        elif tile == ENEMY_TILE_ID:
            enemy = Enemy(rect.x, rect.y, 'enemy', 1.65, 2)
            self._enemy_group.add(enemy)
        elif tile == AMMO_TILE_ID:
            item = ItemBox(rect.x, rect.y, 'ammo')
            self._item_group.add(item)
        elif tile == GRENADE_TILE_ID:
            item = ItemBox(rect.x, rect.y, 'grenade')
            self._item_group.add(item)
        elif tile == HEALTH_TILE_ID:
            item = ItemBox(rect.x, rect.y, 'health')
            self._item_group.add(item)
        elif tile == LEVEL_EXIT_TILE_ID: # level exit
            exit_tile = Exit(img, rect.x, rect.y)
            self._exit_group.add(exit_tile)        


    def load_game_level(self, level=None):
        '''
        Loads the starting world state for the given level.
        '''
        if level is None:
            level = self._current_level

        # Create an empty tile list of the appropriate size for this level
        world_data = []
        for row in range(ROWS):
            empty_row = [-1] * COLS
            world_data.append(empty_row)

        # Read the level data from a CSV file
        with open(f'level{level}_data.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for idx_y, row_of_tiles in enumerate(reader):
                for idx_x, tile_data in enumerate(row_of_tiles):
                    world_data[idx_y][idx_x] = int(tile_data)

        # Populate the world by loading the appropriate game tile
        for idx_y, row in enumerate(world_data):
            for idx_x, tile in enumerate(row):
                if tile >= 0: # -1 is an empty space
                    self.load_game_tile(tile, idx_x, idx_y)
        
        # Nothing really to return here
        return None
    
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

        self.screen_scroll = 0

        # Calculate vertical movement
        sprite.vel_y += GRAVITY
        sprite.vel_y = min(10, sprite.vel_y)
        dy = sprite.vel_y

        # Calculate lateral movement
        dx = sprite.vel_x * sprite.direction.value

        # Detect collisions with wall (x) and ground (y) obstacles
        for tile in self._obstacle_group:
            predicted_x = pygame.Rect(sprite.rect.x + dx, sprite.rect.y, 
                                      sprite.rect.width, sprite.rect.height)
            if tile.rect.colliderect(predicted_x):
                if sprite.direction == Direction.LEFT:
                    sprite.rect.left = tile.rect.right
                elif sprite.direction == Direction.RIGHT:
                    sprite.rect.right = tile.rect.left
            predicted_y = pygame.Rect(sprite.rect.x, sprite.rect.y + dy, 
                                      sprite.rect.width, sprite.rect.height)
            if tile.rect.colliderect(predicted_y):
                if sprite.vel_y < 0:  # jumping and hitting head
                    sprite.vel_y = 0
                    dy = tile.rect.bottom - sprite.rect.top
                if sprite.vel_y > 0:  # landing on surface
                    sprite.landed(sprite.vel_y)
                    dy = tile.rect.top - sprite.rect.bottom

        # If the player is moving too far right or left, scroll the screen
        if (type(sprite) is Player
            and (sprite.direction == Direction.RIGHT and sprite.rect.right >= SCREEN_WIDTH - SCROLL_THRESHOLD
            or sprite.direction == Direction.LEFT and sprite.rect.left < SCROLL_THRESHOLD)):
            self.screen_scroll = -dx
            self.bg_scroll -= self.screen_scroll

        # For everything else, move the sprite
        else:
            sprite.rect.x += dx
            sprite.rect.y += dy


    def draw_text(self, screen, text, color, x, y):
        img = self._font.render(text, True, color)
        screen.blit(img, (x, y))

    def draw(self, screen):

        # Draw the background and the level
        #screen.fill(BG_COLOR)

        #print(self.bg_scroll)
        #bg_image_pairs = zip(self.bg_image_list, self.bg_image_ypos)
        for x in range(5):
            screen.blit(self.bg_image_list[0], ((x * self.bg_width) - self.bg_scroll * 0.5, self.bg_image_ypos[0]))
            screen.blit(self.bg_image_list[1], ((x * self.bg_width) - self.bg_scroll * 0.6, self.bg_image_ypos[1]))
            screen.blit(self.bg_image_list[2], ((x * self.bg_width) - self.bg_scroll * 0.7, self.bg_image_ypos[2]))
            screen.blit(self.bg_image_list[3], ((x * self.bg_width) - self.bg_scroll * 0.8, self.bg_image_ypos[3]))

        for obstacle_tile in self._obstacle_group:
            obstacle_tile.draw(screen, self.screen_scroll)
        for water_tile in self._water_group:
            water_tile.draw(screen, self.screen_scroll)
        for exit_tile in self._exit_group:
            exit_tile.draw(screen, self.screen_scroll)        
        for decoration_tile in self._decoration_group:
            decoration_tile.draw(screen, self.screen_scroll)
        for item_tile in self._item_group:
            item_tile.draw(screen, self.screen_scroll)
        for bullet_tile in self._bullet_group:
            bullet_tile.draw(screen, self.screen_scroll)
        for grenade_tile in self._grenade_group:
            grenade_tile.draw(screen, self.screen_scroll)
        for explosion_tile in self._explosion_group:
            explosion_tile.draw(screen, self.screen_scroll)
        for enemy in self._enemy_group:
            enemy.draw(screen, self.screen_scroll)
        self.player.draw(screen, self.screen_scroll)

        # Draw the status bars
        self.health_bar.draw(screen, self.player.health)
        self.draw_text(screen, f'GRENADES: {self.player.grenades}', WHITE, 10, 35)
        self.draw_text(screen, f'ROUNDS: {self.player.ammo}', WHITE, 10, 60)
        self.draw_text(screen, f'HEALTH: {self.player.health}', WHITE, 10, 85)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        self.rect.x += screen_scroll
        screen.blit(self.image, self.rect)


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        self.rect.x += screen_scroll
        screen.blit(self.image, self.rect)



class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        self.rect.x += screen_scroll
        screen.blit(self.image, self.rect)



class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        self.rect.x += screen_scroll
        screen.blit(self.image, self.rect)
 