import enum
import pygame
import statics


class AttackDirection(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    NONE = 5

class EntityType(enum.Enum):
    PLAYER = 1
    ENEMY = 2
    ITEM = 3
    NPC = 4


class Entity:
    def __init__(self, name:str = "Entity", entity_type: EntityType = EntityType.NPC, starting_pos: tuple = (0, 0), size: int = statics.TILE_SIZE):
        self.name = name
        self.x, self.y = starting_pos
        self.health = 100
        self.entity_type = entity_type
        self.size = size

    def draw(self, screen, camera):
        # Placeholder for drawing logic
        if self.entity_type == EntityType.PLAYER:
            color = statics.PLAYER_COLOR
        elif self.entity_type == EntityType.ENEMY:
            color = statics.ENEMY_COLOR
        elif self.entity_type == EntityType.ITEM:
            color = statics.COIN_COLOR
        elif self.entity_type == EntityType.NPC:
            color = statics.NPC_COLOR
        else:
            color = statics.COLOR_WHITE

        tile_size = statics.TILE_SIZE
        
        tile_x = self.x // tile_size
        tile_y = self.y // tile_size

        # Calculate the center of that tile in world coordinates
        tile_center_x = tile_x * tile_size + tile_size // 2
        tile_center_y = tile_y * tile_size + tile_size // 2
        
        # Check if entity is within camera range before drawing
        screen_width, screen_height = screen.get_size()
        
        # Calculate entity's screen position
        screen_center_x = tile_center_x - camera.x
        screen_center_y = tile_center_y - camera.y
        
        # Check if entity is visible on screen (with some padding for the entity size)
        entity_half_size = self.size // 2
        if (screen_center_x + entity_half_size >= 0 and 
            screen_center_x - entity_half_size <= screen_width and
            screen_center_y + entity_half_size >= 0 and 
            screen_center_y - entity_half_size <= screen_height):
            
            # Draw entity centered at the tile center
            draw_x = screen_center_x - entity_half_size
            draw_y = screen_center_y - entity_half_size

            pygame.draw.rect(screen, color, (draw_x, draw_y, self.size, self.size))
