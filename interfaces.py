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

    def draw_inventory(self, screen, player):
        """Draw the player's inventory on screen."""
        if not self.show_inventory or not player or not hasattr(player, 'inventory'):
            return
        
        # Get inventory items - handle both list and Inventory object
        inventory_items = player.inventory.items if hasattr(player.inventory, 'items') else player.inventory
        
        # Initialize font
        font = pygame.font.Font(None, 24)
        
        # Draw inventory background
        inventory_width = (self.slot_size + self.slot_padding) * 10 + self.slot_padding
        inventory_height = self.slot_size + 2 * self.slot_padding + 30  # Extra space for title
        
        # Background rectangle
        inventory_rect = pygame.Rect(self.inventory_x, self.inventory_y, inventory_width, inventory_height)
        pygame.draw.rect(screen, (50, 50, 50, 180), inventory_rect)
        pygame.draw.rect(screen, (200, 200, 200), inventory_rect, 2)
        
        # Draw title
        title_text = font.render("Inventory", True, (255, 255, 255))
        screen.blit(title_text, (self.inventory_x + 5, self.inventory_y + 5))
        
        # Draw inventory slots
        slot_y = self.inventory_y + 30
        for i in range(10):  # Display up to 10 inventory slots
            slot_x = self.inventory_x + self.slot_padding + i * (self.slot_size + self.slot_padding)
            
            # Draw slot background
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, (80, 80, 80), slot_rect)
            pygame.draw.rect(screen, (150, 150, 150), slot_rect, 1)
            
            # Draw item if it exists
            if i < len(inventory_items):
                item = inventory_items[i]
                if not item.is_disposed():
                    # Draw item representation (small colored square)
                    item_color = statics.COIN_COLOR if item.entity_type == EntityType.ITEM else (255, 255, 255)
                    item_size = self.slot_size - 8
                    item_x = slot_x + 4
                    item_y = slot_y + 4
                    pygame.draw.rect(screen, item_color, (item_x, item_y, item_size, item_size))
                    
                    # Draw item count or type indicator
                    if hasattr(item, 'name') and item.name:
                        # Show first letter of item name
                        text = font.render(item.name[0].upper(), True, (0, 0, 0))
                        text_rect = text.get_rect(center=(slot_x + self.slot_size // 2, slot_y + self.slot_size // 2))
                        screen.blit(text, text_rect)
        
        # Draw inventory count
        count_text = font.render(f"Items: {len(inventory_items)}", True, (255, 255, 255))
        screen.blit(count_text, (self.inventory_x + inventory_width - 100, self.inventory_y + 5))

    def draw(self, screen, player=None):
        """Main UI drawing method."""
        if player:
            self.draw_inventory(screen, player)

    def update(self):
        """Update UI state."""
        pass
        
    def toggle_inventory(self):
        """Toggle inventory visibility."""
        self.show_inventory = not self.show_inventory
