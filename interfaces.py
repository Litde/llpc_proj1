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
    HEALTH = 5



class ImageCache:
    """Singleton class for caching loaded images."""
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_image(cls, path):
        """Get cached image or load and cache it."""
        if path not in cls._cache:
            try:
                cls._cache[path] = pygame.image.load(path).convert_alpha()
            except pygame.error:
                # Return a default colored surface if image fails to load
                cls._cache[path] = pygame.Surface((16, 16))
                cls._cache[path].fill((255, 0, 255))  # Magenta for missing textures
        return cls._cache[path]

    @classmethod
    def clear_cache(cls):
        """Clear all cached images."""
        cls._cache.clear()


class Entity:
    def __init__(self, name:str = "Entity", entity_type: EntityType = EntityType.NPC, starting_pos: tuple = (0, 0), size: int = statics.TILE_SIZE, health: int = 100):
        self.name = name
        self.x, self.y = starting_pos
        self.health = health
        self.entity_type = entity_type
        self.size = size

    def is_disposed(self):
        """Check if this entity has been disposed."""
        return self.entity_type is None

    def draw(self, screen, camera):
        # Don't draw disposed entities
        if self.entity_type is None:
            return

        # Early culling - check if entity is visible before any processing
        if not self._is_visible(screen, camera):
            return

        image = None
        color = None

        # Placeholder for drawing logic
        if self.entity_type == EntityType.PLAYER:
            color = statics.PLAYER_COLOR
        elif self.entity_type == EntityType.ENEMY:
            color = statics.ENEMY_COLOR
        elif self.entity_type == EntityType.ITEM:
            color = statics.COIN_COLOR
        elif self.entity_type == EntityType.NPC:
            color = statics.NPC_COLOR
        elif self.entity_type == EntityType.HEALTH:
            image = ImageCache.get_image(f'{statics.TEXTURES_ROOT}/hearth16x16.png')
        else:
            color = statics.COLOR_WHITE

        # If we have an image, use draw_image method
        if image is not None:
            self.draw_image(screen, camera, image)
            return

        # Draw colored rectangle
        self._draw_colored_rect(screen, camera, color)

    def _is_visible(self, screen, camera):
        """Check if entity is within camera range."""
        screen_width, screen_height = screen.get_size()

        tile_size = statics.TILE_SIZE
        tile_x = self.x // tile_size
        tile_y = self.y // tile_size

        tile_center_x = tile_x * tile_size + tile_size // 2
        tile_center_y = tile_y * tile_size + tile_size // 2

        screen_center_x = tile_center_x - camera.x
        screen_center_y = tile_center_y - camera.y

        entity_half_size = self.size // 2
        return (screen_center_x + entity_half_size >= 0 and
                screen_center_x - entity_half_size <= screen_width and
                screen_center_y + entity_half_size >= 0 and
                screen_center_y - entity_half_size <= screen_height)

    def _draw_colored_rect(self, screen, camera, color):
        """Draw entity as colored rectangle."""
        tile_size = statics.TILE_SIZE
        tile_x = self.x // tile_size
        tile_y = self.y // tile_size

        tile_center_x = tile_x * tile_size + tile_size // 2
        tile_center_y = tile_y * tile_size + tile_size // 2

        screen_center_x = tile_center_x - camera.x
        screen_center_y = tile_center_y - camera.y

        entity_half_size = self.size // 2
        draw_x = screen_center_x - entity_half_size
        draw_y = screen_center_y - entity_half_size

        pygame.draw.rect(screen, color, (draw_x, draw_y, self.size, self.size))

    def draw_image(self, screen, camera, image):
        """Draw the entity using a specific image."""
        if self.entity_type is None or not self._is_visible(screen, camera):
            return

        tile_size = statics.TILE_SIZE
        tile_x = self.x // tile_size
        tile_y = self.y // tile_size

        tile_center_x = tile_x * tile_size + tile_size // 2
        tile_center_y = tile_y * tile_size + tile_size // 2

        screen_center_x = tile_center_x - camera.x
        screen_center_y = tile_center_y - camera.y

        entity_half_size = self.size // 2
        draw_x = screen_center_x - entity_half_size
        draw_y = screen_center_y - entity_half_size

        image_rect = image.get_rect(center=(draw_x + entity_half_size, draw_y + entity_half_size))
        screen.blit(image, image_rect)

    def check_collision(self, other_entity):
        """Check if this entity collides with another entity."""
        # Don't check collisions for disposed entities
        if self.entity_type is None or other_entity.entity_type is None:
            return False
            
        if not isinstance(other_entity, Entity):
            return False
        
        # Check for rectangle collision
        # Since entities are drawn centered on their x,y coordinates,
        # we need to adjust for collision detection by considering the entity's center
        self_left = self.x - self.size // 2
        self_top = self.y - self.size // 2
        self_right = self_left + self.size
        self_bottom = self_top + self.size
        
        other_left = other_entity.x - other_entity.size // 2
        other_top = other_entity.y - other_entity.size // 2
        other_right = other_left + other_entity.size
        other_bottom = other_top + other_entity.size
        
        return (self_left < other_right and
                self_right > other_left and
                self_top < other_bottom and
                self_bottom > other_top)

    def draw_health_bar(self, screen, camera):
        # Don't draw health bar for disposed entities
        if self.entity_type is None:
            return
            
        if self.health <= 0:
            return
        
        # Draw health bar above the entity
        health_bar_width = self.size
        health_bar_height = 5
        health_ratio = self.health / 100.0
        health_bar_color = (255, 0, 0) if self.health < 30 else (0, 255, 0)
        
        tile_size = statics.TILE_SIZE
        
        tile_x = self.x // tile_size
        tile_y = self.y // tile_size

        # Calculate the center of that tile in world coordinates
        tile_center_x = tile_x * tile_size + tile_size // 2
        tile_center_y = tile_y * tile_size + tile_size // 2
        
        # Calculate the screen position of the entity
        screen_center_x = tile_center_x - camera.x
        screen_center_y = tile_center_y - camera.y
        
        # Draw the health bar above the entity
        draw_x = screen_center_x - health_bar_width // 2
        draw_y = screen_center_y - self.size - health_bar_height
        
        pygame.draw.rect(screen, (0, 0, 0), (draw_x, draw_y, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, health_bar_color, (draw_x, draw_y, health_bar_width * health_ratio, health_bar_height))
    
    def dispose(self):
        """Clean up resources and reset entity state."""
        # Prevent double disposal
        if self.entity_type is None:
            return
            
        # Reset entity properties to default/safe values
        self.health = 0
        self.x = 0
        self.y = 0
        self.name = "Disposed Entity"
        
        # Clear any references that might cause memory leaks
        # (In this simple case, there aren't any complex references,
        # but this is where you'd clean up things like:
        # - Event listeners
        # - File handles
        # - Network connections
        # - Custom pygame surfaces
        # - Animation timers, etc.)
        
        # Mark as disposed for debugging
        self.entity_type = None
        

class UI:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.show_inventory = True
        self.inventory_x = 10
        self.inventory_y = 10
        self.slot_size = 40
        self.slot_padding = 5

    def draw(self, screen, player=None):
        """Main UI drawing method."""
        pass

    def update(self):
        """Update UI state."""
        pass
        
    def toggle_inventory(self):
        """Toggle inventory visibility."""
        self.show_inventory = not self.show_inventory
