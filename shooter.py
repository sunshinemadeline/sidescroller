import pygame
from enum import Enum

pygame.init()
pygame.mixer.init()

# Rest of the imports
from button import Button
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS            # type: ignore
from settings import BG_COLOR, PINK, BLACK                       # type: ignore
from world import World                                          # type: ignore
import soldier
import weapons                                                   # type: ignore
from pygame.sprite import spritecollide

# Create the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# Create the main menu
start_button = Button('img/start_btn.png', SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT //2 - 150)
exit_button = Button('img/exit_btn.png', SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT //2 + 50)
DEATH_EVENT = pygame.USEREVENT + 1
LEVEL_EVENT = pygame.USEREVENT + 2

# Required to set the frame rate
clock = pygame.time.Clock()



class Fadetype(Enum):
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
        if self.fade_type == Fadetype.STARTLEVEL:
            #if self.counter <= SCREEN_WIDTH:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0 - self.counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        elif self.fade_type == Fadetype.ENDLEVEL:
            #if self.counter <= SCREEN_WIDTH:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0, 0, self.counter, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH - self.counter, 0, SCREEN_WIDTH // 2 - self.counter, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT - self.counter, SCREEN_WIDTH, self.counter))

        elif self.fade_type == Fadetype.PLAYERDEATH:
            #if self.counter <= SCREEN_HEIGHT:
            self.counter += self.speed
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, self.counter))
        
        if self.counter >= SCREEN_WIDTH:
            self.finished = True


intro_fade = ScreenFade(Fadetype.STARTLEVEL, BLACK, 5)
level_fade = ScreenFade(Fadetype.ENDLEVEL, BLACK, 5)
death_fade = ScreenFade(Fadetype.PLAYERDEATH, PINK, 5)


# Global keyboard action events
mleft_key = False
mright_key = False
jump_key = False
shoot_key = False
throw_key = False

def handle_player_keyboard_events(event: pygame.event.Event) -> None:
    ''' 
    Process player keystrokes and set the global action variables accordingly.
    '''
    global mleft_key, mright_key, jump_key, shoot_key, throw_key
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_a:
            mleft_key = True
        if event.key == pygame.K_d:
            mright_key = True
        if event.key == pygame.K_w:
            jump_key = True
        if event.key == pygame.K_SPACE:
            shoot_key = True
        if event.key == pygame.K_q:
            throw_key = True
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_a:
            mleft_key = False
        if event.key == pygame.K_d:
            mright_key = False
        if event.key == pygame.K_w:
            jump_key = False
        if event.key == pygame.K_SPACE:
            shoot_key = False    
        if event.key == pygame.K_q:
            throw_key = False
    return



def run_main_menu():

    global game_state, game_running
    screen.fill(BG_COLOR)
    start_button.draw(screen)
    exit_button.draw(screen)

    if start_button.is_clicked():
        game_state = "interactive"
        intro_fade.begin_fade()
    if exit_button.is_clicked():
        game_running = False

    # Handle the various inputs to the game
    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                or event.type == pygame.QUIT):
            game_running = False



def run_interactive_game():

    global game_state, game_running
    global level_timer, death_timer
    global world, player

    # Updates all sprites that are governed by the physics engine
    if player.alive:
        if shoot_key and player.ammo > 0 and player.shoot_cooldown == 0:
            bullet = player.shoot()
            world.bullet_group.add(bullet)
        if throw_key and player.grenades > 0 and player.grenade_cooldown == 0:
            grenade = player.throw()
            world.grenade_group.add(grenade)

        player.move(mleft_key, mright_key, jump_key)

        # Handle player animations
        if player.in_air:
            player.update(soldier.Action.JUMP)
        elif (mleft_key and not mright_key 
            or mright_key and not mleft_key):
            player.update(soldier.Action.RUN)
        else:
            player.update(soldier.Action.IDLE)


    # Update the position of all physics-controlled sprites
    world.update()

    world.draw(screen)

    if not intro_fade.finished:
        intro_fade.draw_fade(screen)

    # Check for player death
    if (player.health <= 0 
            or player.rect.top > SCREEN_HEIGHT
            or spritecollide(player, world.water_group, False)):
        if not death_timer:
            death_timer = True
            death_fade.begin_fade()
            pygame.time.set_timer(DEATH_EVENT, 3000)
        if not death_fade.finished:
            death_fade.draw_fade(screen)
        player.death()


    # Handle player levels up
    if pygame.sprite.spritecollideany(world.player, world.exit_group):
        if not level_timer:
            level_timer = True
            level_fade.begin_fade()
            pygame.time.set_timer(LEVEL_EVENT, 3000)
        if not level_fade.finished:
            level_fade.draw_fade(screen)



    # Handle enemy AI controls
    for enemy in world.enemy_group:
        if enemy.alive:
            if (player.alive 
                    and enemy.vision.colliderect(player.rect)
                    and enemy.ammo > 0 
                    and enemy.shoot_cooldown == 0):
                bullet = enemy.ai_shoot()
                world.bullet_group.add(bullet)
            enemy.ai_move()
            if enemy.health <= 0:
                enemy.death()

    # Handle the various inputs to the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_running = False
        elif event.type == DEATH_EVENT:
            world.reset_world()
            world.load_game_level()
            player = world.player
            death_timer = False            
            game_state = "menu"
            pygame.time.set_timer(DEATH_EVENT, 0)
        elif event.type == LEVEL_EVENT:
            world._current_level += 1
            world.reset_world()
            world.load_game_level()
            player = world.player
            level_timer = False
            game_state = "interactive"
            intro_fade.begin_fade()
            pygame.time.set_timer(LEVEL_EVENT, 0)

        handle_player_keyboard_events(event)



if __name__ == '__main__':

    # World variables including a shortcut for the player
    world = World()
    world.load_game_level()
    player = world.player

    death_timer = False
    level_timer = False
    game_state = 'menu'
    game_running = True
    while game_running:
        if game_state == 'menu':
            run_main_menu()
        elif game_state == 'interactive':
            run_interactive_game()
        clock.tick(FPS)
        pygame.display.flip()

    pygame.quit()