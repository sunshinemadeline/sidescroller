from button import Button
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR  # type: ignore
from world import World                                          # type: ignore
import soldier
import weapons                                                   # type: ignore
import pygame
from pygame.sprite import spritecollide

# Create the window
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# Create the main menu
start_button = Button('img/start_btn.png', SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT //2 - 150)
exit_button = Button('img/exit_btn.png', SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT //2 + 50)
RESTART_EVENT = pygame.USEREVENT + 1
LEVEL_EVENT = pygame.USEREVENT + 2

# Required to set the frame rate
clock = pygame.time.Clock()

# Keyboard action events
mleft_key = False
mright_key = False
jump_key = False
shoot_key = False
throw_key = False

def handle_player_keyboard_events(event: pygame.event.Event) -> None:
    ''' 
    Processes keystrokes and sets the global action variables accordingly
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

# World variables including a shortcut for the player
world = World()
world.load_game_level()
player = world.player

# Main game loop
game_state = "menu"
game_running = True
death_timer = False
level_timer = False
while game_running:

    if game_state == "menu":
        screen.fill(BG_COLOR)
        start_button.draw(screen)
        exit_button.draw(screen)

        if start_button.is_clicked():
            game_state = "interactive"
        if exit_button.is_clicked():
            game_running = False

        # Handle the various inputs to the game
        for event in pygame.event.get():
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                    or event.type == pygame.QUIT):
                game_running = False

        clock.tick(FPS)
        pygame.display.flip()                

    else:
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

        # Check if the player collected any item boxes
        for item in pygame.sprite.spritecollide(player, world.item_group, True):
            count = item.quantity
            btype = item.box_type
            if btype == 'ammo':
                player.ammo += min(player.ammo + count, player.max_ammo)
            elif btype == 'grenade':
                player.grenades += min(player.grenades + count, player.max_grenades)
            elif btype == 'health':
                player.health = min(player.health + 25, player.max_health)

        # Check for bullet hit damage
        for bullet in pygame.sprite.spritecollide(player, world.bullet_group, True):
            player.health -= bullet.damage
        for enemy in world.enemy_group:
            for bullet in pygame.sprite.spritecollide(enemy, world.bullet_group, False):
                enemy.health -= bullet.damage
                if enemy.health > 0:
                    bullet.kill()

        # Check for exploding grenades
        for grenade in world.grenade_group:
            if grenade.fuse_timer <= 0:
                # Animate with an explosion
                explosion = weapons.Explosion(grenade.rect.x, grenade.rect.y, 0.75)
                world.explosion_group.add(explosion)
                grenade.kill()
                # Calculate damage against player
                player_damage = grenade.damage_at(player.rect)
                player.health -= player_damage
                # Calcualte damage against each enemy
                for enemy in world.enemy_group:
                    enemy_damage = grenade.damage_at(enemy.rect)
                    enemy.health -= enemy_damage

        # Check for player death
        if (player.health <= 0 
                or player.rect.top > SCREEN_HEIGHT
                or spritecollide(player, world.water_group, False)):
            if not death_timer:
                print("Player died, waiting to return to menu...")
                pygame.time.set_timer(RESTART_EVENT, 2500)
                death_timer = True
            player.death()


        # Handle player levels up
        if pygame.sprite.spritecollideany(world.player, world.exit_group):
            if not level_timer:
                print("Level completed, world resetting...")
                pygame.time.set_timer(LEVEL_EVENT, 2500)
                level_timer = True

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
            elif event.type == RESTART_EVENT:
                world.reset_world()
                world.load_game_level()
                player = world.player
                death_timer = False
                game_state = "menu"
                pygame.time.set_timer(RESTART_EVENT, 0)
            elif event.type == LEVEL_EVENT:
                world._current_level += 1
                world.reset_world()
                world.load_game_level()
                player = world.player
                level_timer = False
                pygame.time.set_timer(LEVEL_EVENT, 0)

            handle_player_keyboard_events(event)

        # Update the game screen at a certain FPS
        world.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()

pygame.quit()