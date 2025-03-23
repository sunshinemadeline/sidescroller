import pygame

pygame.init()
pygame.mixer.init()

# Rest of the imports
from button import GuiButton, ScreenFade, FadeType
from controller import Controller
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS            # type: ignore
from settings import BG_COLOR, PINK, BLACK                       # type: ignore
from world import GameEngine                                     # type: ignore


# Create IO devices: controller for input and graphic screen for output
controller = Controller()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')


# Create the main menu
start_button = GuiButton('img/start_btn.png', SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT //2 - 150)
exit_button = GuiButton('img/exit_btn.png', SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT //2 + 50)
DEATH_EVENT = pygame.USEREVENT + 1
LEVEL_EVENT = pygame.USEREVENT + 2

# Required to set the frame rate
clock = pygame.time.Clock()



intro_fade = ScreenFade(FadeType.STARTLEVEL, BLACK, 5)
level_fade = ScreenFade(FadeType.ENDLEVEL, BLACK, 5)
death_fade = ScreenFade(FadeType.PLAYERDEATH, PINK, 5)



def handle_player_keyboard_events(event: pygame.event.Event, 
                                  controller: Controller) -> Controller:
    ''' 
    Process player keystrokes and returns the current button combination.
    '''

    # Find which keys have been pressed
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_a:
            controller.mleft = True
        if event.key == pygame.K_d:
            controller.mright = True
        if event.key == pygame.K_w:
            controller.jump = True
        if event.key == pygame.K_SPACE:
            controller.shoot = True
        if event.key == pygame.K_q:
            controller.throw = True

    # Find which keys have been released
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_a:
            controller.mleft = False
        if event.key == pygame.K_d:
            controller.mright = False
        if event.key == pygame.K_w:
            controller.jump = False
        if event.key == pygame.K_SPACE:
            controller.shoot = False    
        if event.key == pygame.K_q:
            controller.throw = False
    
    # Return the current state of the controller
    return controller



def run_main_menu(engine, controller, screen):
    '''
    Displays the main menu. This interface is the primary method for human
    players to click on a button and start a new, interactive game.
    '''

    # Draw the main menu
    screen.fill(BG_COLOR)
    start_button.draw(screen)
    exit_button.draw(screen)

    # Handle button clicks
    if start_button.is_clicked():
        engine.game_state = 'interactive'
        engine.load_game_level()
        intro_fade.begin_fade()
    if exit_button.is_clicked():
        engine.game_state = 'quit'

    # Handle the various ways to quit game
    for event in pygame.event.get():
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                or event.type == pygame.QUIT):
            engine.game_state = 'quit'

    # Nothing particularly important to return
    return None



def run_interactive_game(engine, controller, screen):

    global level_timer, death_timer

    # Update the position of all physics-controlled sprites
    engine.update(controller)
    engine.draw(screen)

    # Special case #1: begin a new level
    if not intro_fade.finished:
        intro_fade.draw_fade(screen)

    # Special case #2: player dies, next level
    if not engine.player.alive:
        if not death_timer:
            death_timer = True
            death_fade.begin_fade()
            pygame.time.set_timer(DEATH_EVENT, 3000)
        if not death_fade.finished:
            death_fade.draw_fade(screen)

    # Handle player levels up
    if pygame.sprite.spritecollideany(engine.player, engine.exit_group):
        if not level_timer:
            level_timer = True
            level_fade.begin_fade()
            pygame.time.set_timer(LEVEL_EVENT, 3000)
        if not level_fade.finished:
            level_fade.draw_fade(screen)

    # Handle the various inputs to the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            engine.game_state = 'quit'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            engine.game_state = 'quit'
        elif event.type == DEATH_EVENT:
            engine.reset_world()
            engine.load_game_level()
            death_timer = False            
            engine.game_state = "menu"
            pygame.time.set_timer(DEATH_EVENT, 0)
        elif event.type == LEVEL_EVENT:
            engine._current_level += 1
            engine.reset_world()
            engine.load_game_level()
            level_timer = False
            engine.game_state = "interactive"
            intro_fade.begin_fade()
            pygame.time.set_timer(LEVEL_EVENT, 0)

        controller = handle_player_keyboard_events(event, controller)



if __name__ == '__main__':

    # Global variables for the game
    death_timer = False
    level_timer = False

    # The main game loop has several states, each handled separately:
    #   1. 'Menu' where the player can choose between options
    #   2. 'Interactive' where a human player plays the game
    engine = GameEngine(game_state='menu')
    while engine.game_state != 'quit':
        if engine.game_state == 'menu':
            run_main_menu(engine, controller, screen)
        elif engine.game_state == 'interactive':
            run_interactive_game(engine, controller, screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
