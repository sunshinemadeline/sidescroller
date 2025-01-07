import pygame
import soldier

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.6)

# Importnat game colors
BG_COLOR = (144, 201, 120)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
TILE_SIZE = 100

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

soldier.init()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x, self.y = x, y
        self.health = health
        self.max_health = max_health
    def draw(self, health):
        self.health = health
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))

font = pygame.font.SysFont('Futura', 30)
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


clock = pygame.time.Clock()
FPS = 60

moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

item_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

player = soldier.Soldier(200, 200, 'player', 3)
enemy_group.add(soldier.Soldier(400, 200, 'enemy', 3))
enemy_group.add(soldier.Soldier(500, 200, 'enemy', 3))
item_group.add(soldier.ItemBox(100, 200, 'ammo'))
item_group.add(soldier.ItemBox(600, 200, 'health'))
item_group.add(soldier.ItemBox(650, 200, 'grenade'))

game_running = True
while game_running:
   
    # move the sprites
    if player.alive:
        if shoot:
            player.shoot(bullet_group)
        if grenade and not grenade_thrown:
            player.throw(grenade_group)
            grenade_thrown = True
        player.move(moving_left, moving_right)
        if player.in_air:
            player.update(soldier.Actions.JUMP)
        elif moving_left or moving_right:
            player.update(soldier.Actions.RUN)
        else:
            player.update(soldier.Actions.IDLE)
    else:
        player.update(soldier.Actions.DEATH)
    item_group.update()
    enemy_group.update()
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()

    # check for item boxes
    for box in pygame.sprite.spritecollide(player, item_group, True):
        if box.type == 'ammo':
            player.ammo += 20
            print(player.ammo)
        elif box.type == 'grenade':
            player.grenades += 5
            print(player.grenades)
        elif box.type == 'health':
            player.health = min(player.health + 25, player.max_health)
            print(player.health)

    # check for bullet hits
    for hit in pygame.sprite.spritecollide(player, bullet_group, True):
        player.health -= hit.damage
    for enemy in enemy_group:
        for hit in pygame.sprite.spritecollide(enemy, bullet_group, False):
            enemy.health -= hit.damage
            if enemy.health > 0:
                hit.kill()

    # check for exploding grenades
    for grenade in grenade_group:
        if grenade.timer <= 0:
            explosion = soldier.Explosion(grenade.rect.x, grenade.rect.y, 0.75)
            explosion_group.add(explosion)
            grenade.kill()
            if (abs(grenade.rect.centerx - player.rect.centerx) < grenade.radius * 2
                and abs(grenade.rect.centery - player.rect.centery) < grenade.radius * 2):
                player.health -= grenade.damage
            for enemy in enemy_group:
                if (abs(grenade.rect.centerx - enemy.rect.centerx) < grenade.radius * 2
                    and abs(grenade.rect.centery - enemy.rect.centery) < grenade.radius * 2):
                    enemy.health -= grenade.damage

    # check for death
    if player.health <= 0:
        player.death()
    for enemy in enemy_group:
        if enemy.health <= 0:
            enemy.update(soldier.Actions.DEATH)
            enemy.death()

    # draw the background
    screen.fill(BG_COLOR)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

    draw_text(f'GRENADES: {player.grenades}', font, WHITE, 10, 35)
    draw_text(f'ROUNDS: {player.ammo}', font, WHITE, 10, 60)
    draw_text(f'HEALTH: {player.health}', font, WHITE, 10, 85)

    # draw the sprites
    player.draw(screen)
    item_group.draw(screen)
    enemy_group.draw(screen)
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)

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
                grenade = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False    
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    # update the game screen at a certain FPS
    pygame.display.update()
    clock.tick(FPS)



pygame.quit()