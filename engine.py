
import csv
import pygame
from pygame.sprite import spritecollide
from os.path import exists
from enum import Enum
from soldier import Player, Enemy, Action
from weapons import ItemBox, Explosion
from colors import WHITE, RED, GREEN
from settings import (SCREEN_HEIGHT, SCREEN_WIDTH, SCROLL_RIGHT, SCROLL_LEFT,
                      TILE_SIZE, TILE_TYPE_COUNT,
                      DIRT_TILE_LAST, WATER_TILE_LAST, DECORATION_TILE_LAST,
                      PLAYER_TILE_ID, ENEMY_TILE_ID, AMMO_TILE_ID,
                      GRENADE_TILE_ID, HEALTH_TILE_ID, LEVEL_EXIT_TILE_ID,
                      GRAVITY, Direction)

# TODO: cleanup

class HealthBar():
    '''
    Graphic to visualize the player's health as a green/red rectangle.
    '''

    def __init__(self, x, y, max_health, width=150, height=20):
        '''
        Initializes a player's health bar with the full health value.
        '''
        self.x, self.y = x, y
        self.width = width
        self.height = height
        self.max_health = max_health

    def draw(self, screen, health):
        '''
        Draws the player's health bar to the given screen surface.
        '''
        health_size = self.width * health / self.max_health
        pygame.draw.rect(screen, WHITE, (self.x-1, self.y-1, self.width+2, self.height+2))
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, health_size, self.height))


class GameModes(Enum):
    MENU = 0,
    INTERACTIVE = 1,
    QUIT = 2,

# Intialize sound
pygame.mixer.music.load('audio/music.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 2500)

class GameEngine():

    # Background tiles
    bg_img = [
        pygame.image.load('img/background/sky_cloud.png').convert_alpha(),
        pygame.image.load('img/background/mountain.png').convert_alpha(),
        pygame.image.load('img/background/pine1.png').convert_alpha(),
        pygame.image.load('img/background/pine2.png').convert_alpha()
    ]
    bg_ypos = [
        0,
        SCREEN_HEIGHT - bg_img[1].get_height() - 200,
        SCREEN_HEIGHT - bg_img[2].get_height() - 150,
        SCREEN_HEIGHT - bg_img[3].get_height()
    ]
    bg_width = min([img.get_width() for img in bg_img])

    # Foreground tiles
    tile_img_list = []
    for tile_num in range(TILE_TYPE_COUNT):
        img = pygame.image.load(f'img/tile/{tile_num}.png').convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        tile_img_list.append(img)

    def __init__(self, game_mode=GameModes.MENU):
        '''
        Creates a new world object.
        '''
        self.game_mode = game_mode
        self.current_level = 1
        self.font = pygame.font.SysFont('Futura', 30)

    def reset_world(self):
        ''' 
        Resets the sprites and camera for a new level
        '''
        self.player = None
        self.health_bar = None
        self.obstacle_group = pygame.sprite.Group()
        self.water_group = pygame.sprite.Group()
        self.decoration_group = pygame.sprite.Group()
        self.exit_group = pygame.sprite.Group()
        self.item_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.grenade_group = pygame.sprite.Group()
        self.explosion_group = pygame.sprite.Group()
        self.level_complete = False
        self.camera_scroll = 0
        self.bg_scroll = 0

    def load_game_tile(self, tile, idx_x, idx_y):
        '''
        Loads an individual game tile by creating the tile object and adding
        it to the appropriate sprite group.
        '''
        img = GameEngine.tile_img_list[tile]
        rect = img.get_rect()
        rect.x = idx_x * TILE_SIZE
        rect.y = idx_y * TILE_SIZE

        if tile <= DIRT_TILE_LAST:
            obstacle_tile = Obstacle(img, rect.x, rect.y)
            self.obstacle_group.add(obstacle_tile)
        elif tile <= WATER_TILE_LAST:
            water_tile = Water(img, rect.x, rect.y)
            self.water_group.add(water_tile)
        elif tile <= DECORATION_TILE_LAST:
            decoration_tile = Decoration(img, rect.x, rect.y)
            self.decoration_group.add(decoration_tile)
        elif tile == PLAYER_TILE_ID:
            self.player = Player(rect.x, rect.y, 'player', 1.65)
            self.health_bar = HealthBar(10, 10, self.player.max_health)
        elif tile == ENEMY_TILE_ID:
            enemy = Enemy(rect.x, rect.y, 'enemy', 1.65, 2)
            self.enemy_group.add(enemy)
        elif tile == AMMO_TILE_ID:
            item = ItemBox(rect.x, rect.y, 'ammo')
            self.item_group.add(item)
        elif tile == GRENADE_TILE_ID:
            item = ItemBox(rect.x, rect.y, 'grenade')
            self.item_group.add(item)
        elif tile == HEALTH_TILE_ID:
            item = ItemBox(rect.x, rect.y, 'health')
            self.item_group.add(item)
        elif tile == LEVEL_EXIT_TILE_ID: # level exit
            exit_tile = Exit(img, rect.x, rect.y)
            self.exit_group.add(exit_tile)        


    def load_next_level(self):        
        self.current_level += 1
        if exists(f'level{self.current_level}_data.csv'):
            self.load_current_level()
        else:
            print(f'Error: level {self.current_level} does not exist')
            self.game_mode = GameModes.QUIT

    def load_current_level(self) -> Player:
        '''
        Loads the starting world state for the given level.
        '''
        self.reset_world()

        # Read the level data from a CSV file
        world_data = []
        with open(f'level{self.current_level}_data.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for idx_y, row_of_tiles in enumerate(reader):
                world_data.append([])
                for idx_x, tile_data in enumerate(row_of_tiles):
                    world_data[idx_y].append(int(tile_data))

        # Populate the world by loading the appropriate game tile
        self.world_width = TILE_SIZE * len(world_data[0])
        for idx_y, row_of_tiles in enumerate(world_data):
            for idx_x, tile in enumerate(row_of_tiles):
                if tile >= 0: # -1 is an empty space
                    self.load_game_tile(tile, idx_x, idx_y)
        
        return self.player
    
    def player_actions(self, controller):
        if self.player.alive:
            if controller.shoot and self.player.ammo > 0 and self.player.shoot_cooldown == 0:
                bullet = self.player.shoot()
                self.bullet_group.add(bullet)
            if controller.throw and self.player.grenades > 0 and self.player.grenade_cooldown == 0:
                grenade = self.player.throw()
                self.grenade_group.add(grenade)

            self.player.move(controller.mleft, controller.mright, controller.jump)

            # Handle player animations
            if self.player.in_air:
                self.player.update(Action.JUMP)
            elif (controller.mleft and not controller.mright 
                or controller.mright and not controller.mleft):
                self.player.update(Action.RUN)
            else:
                self.player.update(Action.IDLE)

    def enemy_actions(self):
        # Handle enemy AI controls
        for enemy in self.enemy_group:
            if enemy.alive:
                if (self.player.alive 
                        and enemy.vision.colliderect(self.player.rect)
                        and enemy.ammo > 0 
                        and enemy.shoot_cooldown == 0):
                    bullet = enemy.ai_shoot()
                    self.bullet_group.add(bullet)
                enemy.ai_move()
                if enemy.health <= 0:
                    enemy.death()

    def collect_item_boxes(self):
        ''' 
        Check if player collected any item boxes and add to inventory.
        '''
        for item in spritecollide(self.player, self.item_group, True):
            if item.box_type == 'ammo':
                amount = self.player.ammo + item.quantity
                self.player.ammo += min(amount, self.player.max_ammo)
            elif item.box_type == 'grenade':
                amount = self.player.grenades + item.quantity
                self.player.grenades += min(amount, self.player.max_grenades)
            elif item.box_type == 'health':
                amount = self.player.health + item.quantity
                self.player.health = min(amount, self.player.max_health)

    def handle_bullet_damage(self):
        '''
        Check for bullet hit damage and injure soldier accordingly.
        '''
        for bullet in spritecollide(self.player, self.bullet_group, True):
            self.player.health -= bullet.damage
        for enemy in self.enemy_group:
            for bullet in spritecollide(enemy, self.bullet_group, False):
                enemy.health -= bullet.damage
                if enemy.health >= 0:
                    bullet.kill()        

    def make_grenades_explode(self):
        '''
        Check for exploding grenades and initiate animation.
        '''
        for grenade in self.grenade_group:
            if grenade.fuse_timer <= 0:
                # Animate with an explosion
                explosion = Explosion(grenade.rect.x, grenade.rect.y, 0.75)
                self.explosion_group.add(explosion)
                grenade.kill()
                # Calculate damage against player
                player_damage = grenade.damage_at(self.player.rect)
                self.player.health -= player_damage
                # Calcualte damage against each enemy
                for enemy in self.enemy_group:
                    enemy_damage = grenade.damage_at(enemy.rect)
                    enemy.health -= enemy_damage

    def check_for_player_death(self):
        if (self.player.health <= 0 
                or self.player.rect.top > SCREEN_HEIGHT
                or spritecollide(self.player, self.water_group, False)):
            self.player.death()

    def check_if_level_exit(self):
        if spritecollide(self.player, self.exit_group, False):
            self.level_codrawmplete = True

    def update(self, controller):
        
        # Update based on the player's movements
        self.player_actions(controller)
        self.update_physics(self.player)
        self.update_scrolling()

        # Update all of the other items
        self.enemy_actions()
        for enemy in self.enemy_group:
            self.update_physics(enemy)
        for grenade in self.grenade_group:
            self.update_physics(grenade)
        self.item_group.update()
        self.enemy_group.update(False)
        self.bullet_group.update()
        # Remove any bullet sprites that go past the end of the screen
        for bullet in self.bullet_group:
            if bullet.rect.right < 0 or bullet.rect.left + self.camera_scroll > SCREEN_WIDTH:
                bullet.kill()
        self.grenade_group.update()
        self.explosion_group.update()

        self.collect_item_boxes()
        self.handle_bullet_damage()
        self.make_grenades_explode()
        self.check_for_player_death()
        self.check_if_level_exit()

    def update_scrolling(self):
        # If the player is moving too far right or left, scroll the screen
        if ((self.player.direction == Direction.RIGHT 
                and self.player.rect.right + self.camera_scroll >= SCROLL_RIGHT
                and self.bg_scroll + SCREEN_WIDTH < self.world_width)
            or (self.player.direction == Direction.LEFT 
                and self.player.rect.left + self.camera_scroll < SCROLL_LEFT
                and self.bg_scroll > 0)):
            self.camera_scroll -= self.player.dx
            self.bg_scroll += self.player.dx
        else:
            pass


    def update_physics(self, sprite):
        '''
        Calculates and moves a sprite's position based on its current velocity
        and the effect of gravity.
        '''
        # Calculate vertical movement
        sprite.vel_y += GRAVITY
        sprite.vel_y = min(20, sprite.vel_y)
        sprite.dy = int(sprite.vel_y)

        # Calculate lateral movement
        sprite.dx = int(sprite.vel_x * sprite.direction.value)

        # Detect collisions with wall (x) and ground (y) obstacles
        for tile in self.obstacle_group:
            predicted_x = pygame.Rect(sprite.rect.x + sprite.dx, sprite.rect.y, 
                                      sprite.rect.width, sprite.rect.height)
            if tile.rect.colliderect(predicted_x):
                if sprite.direction == Direction.LEFT:
                    sprite.dx = tile.rect.right - sprite.rect.left
                elif sprite.direction == Direction.RIGHT:
                    sprite.dx = tile.rect.left - sprite.rect.right
                sprite.vel_x = 0
            predicted_y = pygame.Rect(sprite.rect.x, sprite.rect.y + sprite.dy, 
                                      sprite.rect.width, sprite.rect.height)
            if tile.rect.colliderect(predicted_y):
                if sprite.vel_y < 0: # jumping and hitting head
                    sprite.dy = tile.rect.bottom - sprite.rect.top
                if sprite.vel_y > 0:
                    sprite.landed(sprite.vel_y)
                    sprite.dy = tile.rect.top - sprite.rect.bottom
                sprite.vel_y = 0

        # Check if player is going off the edge of the world
        if (sprite.direction == Direction.RIGHT and sprite.rect.right >= self.world_width
                or sprite.direction == Direction.LEFT and sprite.rect.left <= 0):
            sprite.dx = 0

        # Move the sprite and return the distance
        sprite.rect.x += sprite.dx
        sprite.rect.y += sprite.dy
        return


    def draw(self, screen):
        '''
        Blits all of the sprites in the entire world onto the screen.
        '''
        # Draw the background graphics (sky, mountains, trees, etc)
        for x in range(5):
            img_posx = (x * GameEngine.bg_width) - self.bg_scroll * 0.5
            screen.blit(GameEngine.bg_img[0], (img_posx, GameEngine.bg_ypos[0]))
            img_posx = (x * GameEngine.bg_width) - self.bg_scroll * 0.6
            screen.blit(GameEngine.bg_img[1], (img_posx, GameEngine.bg_ypos[1]))
            img_posx = (x * GameEngine.bg_width) - self.bg_scroll * 0.7
            screen.blit(GameEngine.bg_img[2], (img_posx, GameEngine.bg_ypos[2]))
            img_posx = (x * GameEngine.bg_width) - self.bg_scroll * 0.8
            screen.blit(GameEngine.bg_img[3], (img_posx, GameEngine.bg_ypos[3]))

        # Draw the world
        for tile in self.obstacle_group:
            tile.draw(screen, self.camera_scroll)
        for tile in self.water_group:
            tile.draw(screen, self.camera_scroll)
        for tile in self.exit_group:
            tile.draw(screen, self.camera_scroll)        
        for tile in self.decoration_group:
            tile.draw(screen, self.camera_scroll)
        for tile in self.item_group:
            tile.draw(screen, self.camera_scroll)
        for tile in self.bullet_group:
            tile.draw(screen, self.camera_scroll)
        for tile in self.grenade_group:
            tile.draw(screen, self.camera_scroll)
        for tile in self.explosion_group:
            tile.draw(screen, self.camera_scroll)

        # Draw the soldiers
        for tile in self.enemy_group:
            tile.draw(screen, self.camera_scroll)
        self.player.draw(screen, self.camera_scroll)

        # Draw the status bars
        self.health_bar.draw(screen, self.player.health)
        self.draw_text(screen, f'GRENADES: {self.player.grenades}', WHITE, 10, 35)
        self.draw_text(screen, f'ROUNDS: {self.player.ammo}', WHITE, 10, 60)


    def draw_text(self, screen, text, color, x, y):
        img = self.font.render(text, True, color)
        screen.blit(img, (x, y))


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        screen.blit(self.image, (self.rect.x + screen_scroll, self.rect.y))


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        screen.blit(self.image, (self.rect.x + screen_scroll, self.rect.y))



class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        screen.blit(self.image, (self.rect.x + screen_scroll, self.rect.y))



class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, screen, screen_scroll):
        screen.blit(self.image, (self.rect.x + screen_scroll, self.rect.y))
 