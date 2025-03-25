
from enum import IntEnum

# Display screen                                  # TODO: CLeanup
FPS = 60
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.6)
SCROLL_THRESHOLD = SCREEN_WIDTH // 6
SCROLL_RIGHT = SCREEN_WIDTH - SCROLL_THRESHOLD
SCROLL_LEFT = SCROLL_THRESHOLD
SOLDIER_SCALE_VALUE = 1.65

# Environment settings
GRAVITY = 0.75
SOLDIER_JUMP_STRENGTH = -13
BULLET_FULL_DAMAGE = 25
BULLET_VELOCITY_X = 15
GRENADE_FULL_DAMAGE = 100
GRENADE_INNER_RADIUS = 50  # pixels from grenade
GRENADE_OUTER_RADIUS = 200 # pixels from grenade
GRENADE_VELOCITY_X = 7
GRENADE_VELOCITY_Y = -11
GRENADE_FUSE_TIME = 1500
PLAYER_SHOOT_DELAY = 200
PLAYER_THROW_DELAY = 1500
SOLDIER_SHOOT_DELAY = 1500
SOLDIER_THROW_DELAY = 3000
ANIMATION_DELAY = 100

# Gamemap tiles
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS # this should be defined for the size of images instead of hardcoded 16
TILE_TYPE_COUNT = 21
DIRT_TILE_FIRST = 0
DIRT_TILE_LAST = 8
WATER_TILE_FIRST = 9
WATER_TILE_LAST = 10
DECORATION_TILE_FIRST = 11
DECORATION_TILE_LAST = 14
PLAYER_TILE_ID = 15
ENEMY_TILE_ID = 16
AMMO_TILE_ID = 17
GRENADE_TILE_ID = 18
HEALTH_TILE_ID = 19
LEVEL_EXIT_TILE_ID = 20

# Soldier animations
class Action(IntEnum):
    IDLE = 0
    RUN = 1
    JUMP = 2
    DEATH = 3

class Direction(IntEnum):
    LEFT = -1
    RIGHT = 1
    IDLE = 0
    def reverse(self):
        return Direction(-self.value)
    def pause(self):
        return Direction(0)
    def __mul__(self, operand):
        if operand == -1:
            return Direction(-self.value)
        raise ValueError("Multiplication only support -1 to reverse direction")
