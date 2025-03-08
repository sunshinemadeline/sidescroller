
from settings import BG_COLOR, RED, WHITE                         # type: ignore
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS             # type: ignore
from settings import ROWS, COLS, TILE_SIZE, TILE_TYPES            # type: ignore
from world import World                                           # type: ignore
import pygame
import soldier
import weapons                                                    # type: ignore

# Create the window
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# Required to set the frame rate
clock = pygame.time.Clock()

# Keyboard events
moving_left = False
moving_right = False
jumping = False
shoot = False
throw = False

# World variables
level = 1
world = World()
world.load_game_level(level)
player = world.player

# Main game loop
game_running = True
while game_running:
   
    # Update the position of all physics-controlled sprites
    world.update_physics()

    # Updates all sprites that are governed by the physics engine
    if player.alive:
        if shoot and player.ammo > 0 and player.shoot_cooldown == 0:
            bullet = player.shoot()
            world.bullet_group.add(bullet)
        if throw and player.grenades > 0 and player.grenade_cooldown == 0:
            grenade = player.throw()
            world.grenade_group.add(grenade)

        player.move(moving_left, moving_right, jumping)

        # Handle player animations
        if player.in_air:
            player.update(soldier.Action.JUMP)
        elif (moving_left and not moving_right 
              or moving_right and not moving_left):
            player.update(soldier.Action.RUN)
        else:
            player.update(soldier.Action.IDLE)

    # Update all of the non-player sprites
    world.item_group.update()
    world.enemy_group.update()
    world.bullet_group.update()
    world.grenade_group.update()
    world.explosion_group.update()

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

    # Check for bullet hits
    for bullet in pygame.sprite.spritecollide(player, world.bullet_group, True):
        player.health -= bullet.damage
    for enemy in world.enemy_group:
        for bullet in pygame.sprite.spritecollide(enemy, world.bullet_group, False):
            enemy.health -= bullet.damage
            if enemy.health > 0:
                bullet.kill()

    # Remove sprites that go past the end of the screen
    for bullet in world.bullet_group:
        if bullet.rect.right < 0 or bullet.rect.left > SCREEN_WIDTH:
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
    if player.health <= 0:
        player.update(soldier.Action.DEATH)
        player.death()


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
                enemy.update(soldier.Action.DEATH)
                enemy.death()

    world.draw(screen)

    for event in pygame.event.get():

        # Quit event for mouse click on [X] box
        if event.type == pygame.QUIT:
            game_running = False
        
        # Game controller
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_running = False
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w: # TODO: more consistent logic loop vs soldier class
                jumping = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                throw = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                jumping = False
            if event.key == pygame.K_SPACE:
                shoot = False    
            if event.key == pygame.K_q:
                throw = False

    # update the game screen at a certain FPS
    pygame.display.update()
    clock.tick(FPS)



pygame.quit()