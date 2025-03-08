
from settings import BG_COLOR, RED, WHITE                         # type: ignore
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS             # type: ignore
from settings import ROWS, COLS, TILE_SIZE, TILE_TYPES            # type: ignore
from world import World                                           # type: ignore
import pygame
import soldier

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

soldier.init()

font = pygame.font.SysFont('Futura', 30)
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

clock = pygame.time.Clock()

level = 1


moving_left = False
moving_right = False
shoot = False
throw = False


world = World()
world.load_game_level(level)
player = world.player


game_running = True
while game_running:
   
    # Updates all sprites that are governed by the physics engine
    if player.alive:
        if shoot and player.ammo > 0 and player.shoot_cooldown == 0:
            bullet = player.shoot()
            world.bullet_group.add(bullet)
        if throw and player.grenades > 0 and player.grenade_cooldown == 0:
            grenade = player.throw()
            world.grenade_group.add(grenade)
        player.move(moving_left, moving_right)

        # Handle player animations
        if player.in_air:
            player.update(soldier.Action.JUMP)
        elif moving_left or moving_right:
            player.update(soldier.Action.RUN)
        else:
            player.update(soldier.Action.IDLE)
    
    world.enemy_group.update()
    world.grenade_group.update()

    # Update all of the sprites that are unaffected by physics
    world.item_group.update()
    world.bullet_group.update()
    world.explosion_group.update()

    # Check if the player collected any item boxes
    for box in pygame.sprite.spritecollide(player, world.item_group, True):
        if box.type == 'ammo':
            player.ammo += 20
        elif box.type == 'grenade':
            player.grenades += 5
        elif box.type == 'health':
            player.health = min(player.health + 25, player.max_health)

    # Check for bullet hits
    for bullet in pygame.sprite.spritecollide(player, world.bullet_group, True):
        player.health -= bullet.damage
    for enemy in world.enemy_group:
        for bullet in pygame.sprite.spritecollide(enemy, world.bullet_group, False):
            enemy.health -= bullet.damage
            if enemy.health > 0:
                bullet.kill()

    # Check for exploding grenades
    for grenade in world.grenade_group:
        if grenade.timer <= 0:
            # Animate with an explosion
            explosion = soldier.Explosion(grenade.rect.x, grenade.rect.y, 0.75)
            world.explosion_group.add(explosion)
            grenade.kill()
            # Calculate damage against player
            player_damage = grenade.damage(player.rect)
            player.health -= player_damage
            # Calcualte damage against each enemy
            for enemy in world.enemy_group:
                enemy_damage = grenade.damage(enemy.rect)
                enemy.health -= enemy_damage

    # Check for player death
    if player.health <= 0:
        player.update(soldier.Action.DEATH)
        player.death()

    # Draw the background and the level
    screen.fill(BG_COLOR)
    world.draw(screen)

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

    # Draw the status bars
    world.health_bar.draw(screen, player.health)
    draw_text(f'GRENADES: {player.grenades}', font, WHITE, 10, 35)
    draw_text(f'ROUNDS: {player.ammo}', font, WHITE, 10, 60)
    draw_text(f'HEALTH: {player.health}', font, WHITE, 10, 85)

    # Draw the sprites
    world.item_group.draw(screen)
    world.bullet_group.draw(screen)
    world.grenade_group.draw(screen)
    world.explosion_group.draw(screen)
    world.decoration_group.draw(screen)
    world.water_group.draw(screen)
    world.exit_group.draw(screen)
    for enemy in world.enemy_group:
        enemy.draw(screen)
    player.draw(screen)

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
            if event.key == pygame.K_w and player.alive: # TODO: more consistent logic loop vs soldier class
                player.jump = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                throw = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False    
            if event.key == pygame.K_q:
                throw = False

    # update the game screen at a certain FPS
    pygame.display.update()
    clock.tick(FPS)



pygame.quit()