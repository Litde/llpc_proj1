MAPS_ROOT = "maps"
TEXTURES_ROOT = "textures"
TILE_SIZE = 32
PLAYER_SIZE = 20
PLAYER_SPEED = TILE_SIZE
PLAYER_ATTACK_RADIUS = TILE_SIZE * 2
PLAYER_STARTING_POSITION = (200, 200)  # Example starting position
PLAYER_COLOR = (255, 0, 0)  
ATTACK_COLOR = (255, 0, 0)
ATTACK_DAMAGE = 50
ATTACK_DURATION_FRAMES = 30  # Attack visible for 30 frames
COIN_COLOR = (255, 215, 0)  # Gold color for coins
COIN_SIZE = 10
NPC_COLOR = (0, 255, 0)  # Green for NPCs
ENEMY_COLOR = (255, 0, 0)  # Red for enemies
ENEMY_STARTING_POSITION = (100, 100)  # Example enemy starting position
ENEMY_SIZE = 20
ENEMY_SPEED = 0.75  # Much slower movement - 1 pixel per frame
ENEMY_AGGRO_RADIUS = TILE_SIZE * 5  # Enemies will chase player within this radius
ENEMY_DAMAGE = 10
FPS = 60
MAP_WIDTH = 1920
MAP_HEIGHT = 1080

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)


TILE_VALUES = {
    0: "empty",
    1: "water",
    2: "floor",
    3: "grass",
}