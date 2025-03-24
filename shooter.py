
# Initialize the display and sound before importing any other modules
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
pygame.init()
pygame.mixer.init()
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# Now import the other modules, which may depend on the mixer and display
from controller import GameController
from widgets import GameButton, GameFade, FadeType, BG_COLOR, PINK, BLACK
from engine import GameEngine

# Create IO devices:
#  1) controller for input
#  2) graphic display for output
#  3) a clock to keep time
controller = GameController()
engine = GameEngine()
screen = pygame.display.get_surface()
clock = pygame.time.Clock()


def handle_keyboard_events(event: pygame.event.Event, 
                           controller: GameController) -> GameController:
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



def run_main_menu(engine: GameEngine, 
                  controller: GameController, 
                  screen: pygame.Surface) -> None:
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



def run_interactive_game(engine: GameEngine,                    # TODO: Add docstring
                         controller: GameController, 
                         screen: pygame.Surface) -> None:

    # Update the position of all physics-controlled sprites
    engine.update(controller)
    engine.draw(screen)

    # Special case #1: begin a new level
    if not intro_fade.finished:
        intro_fade.draw_fade(screen)

    # Special case #2: player dies, restart same level
    if not engine.player.alive:
        if not death_fade.started:
            death_fade.begin_fade()
            pygame.time.set_timer(DEATH_EVENT, 3000)
        if not death_fade.finished:
            death_fade.draw_fade(screen)

    # Special case #3: player advances to the next level
    if pygame.sprite.spritecollideany(engine.player, engine.exit_group):
        if not level_fade.started:                    # TODO: Move to game engine and create variable
            level_fade.begin_fade()                   # for next level that is always triggered
            pygame.time.set_timer(LEVEL_EVENT, 3000)
        if not level_fade.finished:
            level_fade.draw_fade(screen)

    # Handle the various controller inputs to the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            engine.game_state = 'quit'
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            engine.game_state = 'quit'
        elif event.type == DEATH_EVENT:
            engine.reset_world()
            engine.load_game_level()
            engine.game_state = "menu"               # TODO: Enum
            pygame.time.set_timer(DEATH_EVENT, 0)    # TODO: Can we get rid of timers?
        elif event.type == LEVEL_EVENT:
            engine._current_level += 1               # TODO: Add function?
            engine.reset_world()
            engine.load_game_level()
            engine.game_state = "interactive"
            intro_fade.begin_fade()
            pygame.time.set_timer(LEVEL_EVENT, 0)

        controller = handle_keyboard_events(event, controller)

    # Nothing particularly important to return
    return None



if __name__ == '__main__':

    # Create the buttons for use on the main menudisplay
    start_button_img = pygame.image.load('img/start_btn.png').convert_alpha()
    start_button_x = SCREEN_WIDTH // 2 - start_button_img.get_width() // 2
    start_button_y = SCREEN_HEIGHT // 2 - start_button_img.get_height() - 100
    start_button = GameButton(start_button_img, start_button_x, start_button_y)
    exit_button_img = pygame.image.load('img/exit_btn.png').convert_alpha()
    exit_button_x = SCREEN_WIDTH // 2 - exit_button_img.get_width() // 2
    exit_button_y = SCREEN_HEIGHT // 2 - exit_button_img.get_height() + 100
    exit_button = GameButton(exit_button_img, exit_button_x, exit_button_y)

    # Define notable game events and their transitions
    INTRO_EVENT = pygame.USEREVENT + 1
    LEVEL_EVENT = pygame.USEREVENT + 2
    DEATH_EVENT = pygame.USEREVENT + 3
    intro_fade = GameFade(FadeType.INTRO_EVENT, BLACK)
    level_fade = GameFade(FadeType.LEVEL_EVENT, BLACK)   # TODO: Fix level fade
    death_fade = GameFade(FadeType.DEATH_EVENT, PINK)

    # The main game loop has several states, each handled separately:
    #   1. 'Menu' where the player can choose between options
    #   2. 'Interactive' where a human player plays the game
    while engine.game_state != 'quit':
        if engine.game_state == 'menu':
            run_main_menu(engine, controller, screen)
        elif engine.game_state == 'interactive':
            run_interactive_game(engine, controller, screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
