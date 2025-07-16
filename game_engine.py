import random
import statics
import pygame
import pygame, os
from interfaces import AttackDirection, EntityType, Entity, UI

os.environ['SDL_VIDEO_CENTERED'] = '1'





class GameEngine:
    def __init__(self, is_map_editor:bool = False, display_camera_location:bool = False):
        self.game_logic = GameLogic(self)
        self.player = Player(self)
        self.camera = Camera(display_camera_location=display_camera_location)
        self.map_engine = MapEngine(self)
        self.is_map_editor = is_map_editor
        self.initialized = False
        
        pygame.init()
        pygame.display.set_caption("Game Engine Example")
        
        self.initialize()


    def initialize(self):
        self.player.reset()
        self.camera.reset()
        self.map_engine.initialize()
        if not self.is_map_editor:
            self.game_logic.add_entities([self.player])
        self.initialized = True

    def reset(self):
        self.game_logic.reset()
        self.map_engine.reset()
        self.player.reset()
        self.camera.reset()
        self.initialized = False

    def reset_player(self):
        """Reset just the player without affecting other game state."""
        # Reset player state
        self.player.reset()
        
        # Ensure player is in the entities list
        if self.player not in self.game_logic.entities:
            self.game_logic.entities.append(self.player)
        
        # Clear any damage tracking that might affect the player
        self.map_engine.damaged_entities_this_attack.clear()


class GameLogic:
    def __init__(self, game_engine: GameEngine):
        self.clock = pygame.time.Clock()
        self.fps = statics.FPS
        self.clock.tick(self.fps)
        self.game_engine = game_engine
        self.entities = []

    def create_entity(self, name: str = "Entity", entity_type: EntityType = EntityType.NPC, starting_pos: tuple = (0, 0), size: int = statics.TILE_SIZE, health: int = 100):
        """Creates a new entity with the given parameters."""
        if entity_type == EntityType.ENEMY:
            # Create Enemy instance for proper AI behavior
            entity = Enemy(self.game_engine, name=name, starting_pos=starting_pos, size=size)
            entity.health = health  # Set custom health if provided
        else:
            # Create generic Entity for other types
            entity = Entity(name=name, entity_type=entity_type, starting_pos=starting_pos, size=size, health=health)
        
        self.entities.append(entity)
        return entity

    def add_entities(self, entities):
        """Extends the game with entities."""
        self.entities.extend(entities)

    def populate_entities(self, num_entities: int = 10, entity_type: EntityType = EntityType.ITEM, size: int = statics.TILE_SIZE, health: int = 100):
        """Populates the game with a specified number of entities."""
        # Use actual map dimensions instead of static constants
        if self.game_engine.map_engine.map_data:
            map_width_tiles = len(self.game_engine.map_engine.map_data[0])
            map_height_tiles = len(self.game_engine.map_engine.map_data)
            map_width_pixels = map_width_tiles * statics.TILE_SIZE
            map_height_pixels = map_height_tiles * statics.TILE_SIZE
        else:
            # Fallback to static constants if no map is loaded
            map_width_pixels = statics.MAP_WIDTH
            map_height_pixels = statics.MAP_HEIGHT
        
        for i in range(num_entities):
            # Generate random tile coordinates
            tile_occupied = False
            while not tile_occupied:
                tile_x = random.randint(0, map_width_pixels // statics.TILE_SIZE - 1)
                tile_y = random.randint(0, map_height_pixels // statics.TILE_SIZE - 1)

                # Check if the tile is already occupied
                tile_occupied = not self.game_engine.map_engine.is_tile_occupied(tile_x, tile_y)

            # Position entity at the center of the tile
            center_x = tile_x * statics.TILE_SIZE + statics.TILE_SIZE // 2
            center_y = tile_y * statics.TILE_SIZE + statics.TILE_SIZE // 2
            
            self.create_entity(name=f"Entity {i}", entity_type=entity_type, 
                             starting_pos=(center_x, center_y), 
                             size=size,
                             health=health)

    def reset(self):
        self.clock = pygame.time.Clock()
        self.fps = statics.FPS
        self.clock.tick(self.fps)
        self.entities.clear()

    def cleanup_disposed_entities(self):
        """Remove disposed entities from the entities list to prevent memory leaks."""
        self.entities = [entity for entity in self.entities if not entity.is_disposed()]

    def dispose_entity(self, entity):
        """Dispose an entity and schedule it for removal."""
        if entity in self.entities:
            entity.dispose()

    def pickup_coin(self, player):
        """Handles picking up a coin entity."""
        for coin in self.entities:
            if not coin.is_disposed() and coin.entity_type == EntityType.ITEM:
                if player.check_collision(coin):
                    self.entities.remove(coin)
                    player.inventory.append(coin)
                    coin.dispose()

    def deal_damage(self, player, attack_direction, attack_timer, damaged_entities_this_attack, damage=statics.ATTACK_DAMAGE):
        """Deals damage to entities in the attack area based on attack direction."""
        if player.is_disposed() or attack_timer <= 0:
            return
        
        # Calculate player position (centered in tile)
        tile_size = statics.TILE_SIZE
        player_tile_x = player.x // tile_size
        player_tile_y = player.y // tile_size
        player_center_x = player_tile_x * tile_size + tile_size // 2
        player_center_y = player_tile_y * tile_size + tile_size // 2
        
        # Define attack area based on direction
        attack_range = statics.PLAYER_ATTACK_RADIUS
        attack_thickness = tile_size  # Make attack area tile-width thick
        attack_rect = None
        
        if attack_direction == AttackDirection.UP:
            attack_rect = pygame.Rect(
                player_center_x - attack_thickness // 2,
                player_center_y - attack_range,
                attack_thickness, 
                attack_range
            )
        elif attack_direction == AttackDirection.DOWN:
            attack_rect = pygame.Rect(
                player_center_x - attack_thickness // 2,
                player_center_y,
                attack_thickness,
                attack_range
            )
        elif attack_direction == AttackDirection.LEFT:
            attack_rect = pygame.Rect(
                player_center_x - attack_range,
                player_center_y - attack_thickness // 2,
                attack_range,
                attack_thickness
            )
        elif attack_direction == AttackDirection.RIGHT:
            attack_rect = pygame.Rect(
                player_center_x,
                player_center_y - attack_thickness // 2,
                attack_range,
                attack_thickness
            )
        
        if attack_rect is None:
            return
        
        # Check collision with entities in the attack area
        for entity in self.entities:
            if (not entity.is_disposed() and 
                entity.entity_type != EntityType.PLAYER and 
                entity.entity_type != EntityType.ITEM and  # Don't attack items/coins
                entity not in damaged_entities_this_attack):  # Only damage each entity once per attack
                
                # Create entity rectangle centered on entity position
                entity_rect = pygame.Rect(
                    entity.x - entity.size // 2,
                    entity.y - entity.size // 2,
                    entity.size,
                    entity.size
                )
                
                # Check if attack area intersects with entity
                if attack_rect.colliderect(entity_rect):
                    # Mark this entity as damaged in this attack
                    damaged_entities_this_attack.add(entity)
                    entity.health -= damage
                    if entity.health <= 0:
                        self.dispose_entity(entity)


class MapEngine:
    def __init__(self, game_engine: GameEngine, map_path:str=None):
        self.map_data = self.load_map(map_path) if map_path else None
        self.seed = None
        self.screen = None
        self.game_engine = game_engine
        self.initialized = False
        
        # Attack timer system
        self.attack_timer = 0
        self.current_attack_direction = AttackDirection.NONE
        self.damaged_entities_this_attack = set()  # Track entities damaged in current attack

        self.initialize()

    def initialize(self, windows_size:tuple=(800, 600)):
        self.screen = pygame.display.set_mode(windows_size)
        # Set player position to the center of the starting tile
        tile_size = statics.TILE_SIZE
        start_x = statics.PLAYER_STARTING_POSITION[0] + tile_size // 2
        start_y = statics.PLAYER_STARTING_POSITION[1] + tile_size // 2
        self.game_engine.player.x = start_x
        self.game_engine.player.y = start_y

        self.initialized = True

    def reset(self):
        self.map_data = None
        self.seed = None
        self.screen = None
        self.initialized = False
        self.attack_timer = 0
        self.current_attack_direction = AttackDirection.NONE
        self.damaged_entities_this_attack = set()


    def generate_seeded_map(self, seed=None, width=20, height=20):
        if seed is not None:
            self.seed = seed
        if self.seed is not None:
            random.seed(self.seed)

        self.width = width
        self.height = height

        # Generate basic terrain map with different tile types
        # 0 = grass, 1 = water, 2 = mountain, 3 = forest
        terrain_map = []

        for y in range(height):
            row = []
            for x in range(width):
                # Use position-based probability for varied terrain
                distance_from_center = ((x - width//2)**2 + (y - height//2)**2)**0.5

                rand_val = random.random()

                if distance_from_center > width * 0.3:
                    # Outer areas more likely to be mountains or water
                    if rand_val < 0.3:
                        tile = 2  # mountain
                    elif rand_val < 0.5:
                        tile = 1  # water
                    elif rand_val < 0.8:
                        tile = 3  # forest
                    else:
                        tile = 0  # grass
                else:
                    # Center areas more likely to be traversable
                    if rand_val < 0.6:
                        tile = 0  # grass
                    elif rand_val < 0.8:
                        tile = 3  # forest
                    elif rand_val < 0.9:
                        tile = 1  # water
                    else:
                        tile = 2  # mountain

                row.append(tile)
            terrain_map.append(row)

        self.map_data = terrain_map
        return terrain_map

    def generate_random_map(self, width=20, height=20):
        return self.generate_seeded_map(seed=None, width=width, height=height)
    
    def generate_map_in_proportions_of_screen(self):
        if not self.initialized:
            raise RuntimeError("Screen not initialized. Call initialize() first.")

        screen_width, screen_height = self.screen.get_size()
        tile_size = statics.TILE_SIZE

        width = screen_width // tile_size
        height = screen_height // tile_size

        return self.generate_seeded_map(seed=None, width=width, height=height)

    def save_map(self, name="random_map") -> None:
        with open(f"{statics.MAPS_ROOT}/{name}", 'w') as f:
            for row in self.map_data:
                f.write(' '.join(str(tile) for tile in row) + '\n')

    def load_map(self, map_path: str) -> None:
        """Loads a map from a specified file path."""
        self.map_data = []
        try:
            with open(f'{statics.MAPS_ROOT}/{map_path}', 'r') as f:
                for line in f:
                    row = list(map(int, line.strip().split()))
                    self.map_data.append(row)
        except FileNotFoundError:
            raise FileNotFoundError(f"Map file '{map_path}' not found.")
        except Exception as e:
            raise RuntimeError(f"Error loading map: {e}")
        
        return len(self.map_data[0]) if self.map_data else 0, len(self.map_data) if self.map_data else 0
    
    def change_tile(self, tile_x: int, tile_y: int, new_tile_type: str):
        """
        Change the tile at the specified coordinates to a new tile type.
        """
        if not self.map_data:
            raise ValueError("No map data available to change tiles.")
        
        if tile_y < 0 or tile_y >= len(self.map_data) or tile_x < 0 or tile_x >= len(self.map_data[0]):
            raise IndexError("Tile coordinates out of bounds.")
        
        # Convert new_tile_type to integer
        try:
            new_tile_type = int(new_tile_type)
        except ValueError:
            raise ValueError("Invalid tile type. Must be an integer.")

        self.map_data[tile_y][tile_x] = new_tile_type

    def is_tile_occupied(self, tile_x: int, tile_y: int) -> bool:
        """
        Check if a tile at the specified coordinates is occupied by an entity.
        """
        if not self.game_engine or not self.game_engine.game_logic:
            return False

        is_water = self.map_data[tile_y][tile_x] == list(statics.TILE_VALUES.keys())[1]

        for entity in self.game_engine.game_logic.entities:
            if (entity.x // statics.TILE_SIZE == tile_x and 
                entity.y // statics.TILE_SIZE == tile_y and 
                not entity.is_disposed()) or is_water:
                return True
        return False

    def draw_map(self):
        if self.map_data is None:
            raise ValueError("No map data available to display.")

        tile_colors = {
            0: (50, 150, 50),  # grass - green
            1: (50, 50, 150),  # water - blue
            2: (100, 100, 100),  # mountain - gray
            3: (0, 100, 0)  # forest - dark green
        }

        tile_size = statics.TILE_SIZE
        screen_width, screen_height = self.screen.get_size()
        
        # Calculate camera offset
        camera_x = self.game_engine.camera.x
        camera_y = self.game_engine.camera.y
        
        # Calculate which tiles need to be drawn on screen (including beyond map boundaries)
        start_tile_x = camera_x // tile_size
        start_tile_y = camera_y // tile_size
        end_tile_x = (camera_x + screen_width) // tile_size + 1
        end_tile_y = (camera_y + screen_height) // tile_size + 1

        # Draw all visible tiles (including black squares beyond map boundaries)
        for y in range(start_tile_y, end_tile_y):
            for x in range(start_tile_x, end_tile_x):
                # Check if tile is within map boundaries
                if (0 <= y < len(self.map_data) and 0 <= x < len(self.map_data[0])):
                    # Draw map tile
                    tile_type = self.map_data[y][x]
                    color = tile_colors.get(tile_type, (255, 255, 255))
                else:
                    # Draw black square beyond map boundaries
                    color = (0, 0, 0)

                # Calculate screen position relative to camera
                screen_x = x * tile_size - camera_x
                screen_y = y * tile_size - camera_y

                pygame.draw.rect(self.screen, color,
                                 (screen_x, screen_y, tile_size, tile_size))

    # def draw_player(self):
        """Draws the player on the map."""
        if self.game_engine.initialized and self.game_engine.player:
            player_color = statics.PLAYER_COLOR
            player_size = statics.PLAYER_SIZE
            tile_size = statics.TILE_SIZE
            
            # Calculate which tile the player is currently in
            tile_x = self.game_engine.player.x // tile_size
            tile_y = self.game_engine.player.y // tile_size
            
            # Calculate the center of that tile in world coordinates
            tile_center_x = tile_x * tile_size + tile_size // 2
            tile_center_y = tile_y * tile_size + tile_size // 2
            
            # Calculate screen position relative to camera
            screen_center_x = tile_center_x - self.game_engine.camera.x
            screen_center_y = tile_center_y - self.game_engine.camera.y
            
            # Draw player centered at the tile center
            draw_x = screen_center_x - player_size // 2
            draw_y = screen_center_y - player_size // 2
            
            pygame.draw.rect(self.screen, player_color,
                             (draw_x, draw_y, player_size, player_size))

    def draw_camera(self):
        """Draws the camera view on the map."""
        if self.game_engine.initialized and self.game_engine.camera.display_camera_location:
            camera_color = (255, 255, 0)
            # Draw camera border around the screen edges to show the viewport
            pygame.draw.rect(self.screen, camera_color, 
                           (0, 0, self.screen.get_width(), self.screen.get_height()), 2)

    def draw_game_starting_position(self):
        """Draws the game starting position on the map."""
        if self.game_engine.initialized and self.game_engine.player:
            starting_color = (255, 255, 0)
            tile_size = statics.TILE_SIZE
            player_size = statics.PLAYER_SIZE
            
            # Calculate which tile the starting position is in (same logic as draw_player)
            tile_x = statics.PLAYER_STARTING_POSITION[0] // tile_size
            tile_y = statics.PLAYER_STARTING_POSITION[1] // tile_size
            
            # Calculate the center of that tile in world coordinates
            tile_center_x = tile_x * tile_size + tile_size // 2
            tile_center_y = tile_y * tile_size + tile_size // 2
            
            # Calculate screen position relative to camera
            screen_center_x = tile_center_x - self.game_engine.camera.x
            screen_center_y = tile_center_y - self.game_engine.camera.y
            
            # Draw starting position centered at the tile center
            draw_x = screen_center_x - player_size // 2
            draw_y = screen_center_y - player_size // 2
            
            starting_rect = pygame.Rect(draw_x, draw_y, player_size, player_size)
            pygame.draw.rect(self.screen, starting_color, starting_rect)

    def draw_attack(self, attack_direction):
        """Draws the attack area around the player."""
        if self.game_engine.initialized and self.game_engine.player:
            attack_color = statics.ATTACK_COLOR
            attack_range = statics.PLAYER_ATTACK_RADIUS
            tile_size = statics.TILE_SIZE
            attack_thickness = 8  # Thickness of the attack rectangle
            
            # Calculate which tile the player is currently in (same as draw_player)
            tile_x = self.game_engine.player.x // tile_size
            tile_y = self.game_engine.player.y // tile_size
            
            # Calculate the center of that tile in world coordinates
            tile_center_x = tile_x * tile_size + tile_size // 2
            tile_center_y = tile_y * tile_size + tile_size // 2
            
            # Calculate screen position relative to camera
            screen_center_x = tile_center_x - self.game_engine.camera.x
            screen_center_y = tile_center_y - self.game_engine.camera.y
            
            if attack_direction == AttackDirection.UP:
                pygame.draw.rect(self.screen, attack_color,
                                 (screen_center_x - attack_thickness // 2,
                                  screen_center_y - attack_range,
                                  attack_thickness, attack_range))
            elif attack_direction == AttackDirection.DOWN:
                pygame.draw.rect(self.screen, attack_color,
                                 (screen_center_x - attack_thickness // 2,
                                  screen_center_y,
                                  attack_thickness, attack_range))
            elif attack_direction == AttackDirection.LEFT:
                pygame.draw.rect(self.screen, attack_color,
                                 (screen_center_x - attack_range,
                                  screen_center_y - attack_thickness // 2,
                                  attack_range, attack_thickness))
            elif attack_direction == AttackDirection.RIGHT:
                pygame.draw.rect(self.screen, attack_color,
                                 (screen_center_x,
                                  screen_center_y - attack_thickness // 2,
                                  attack_range, attack_thickness))  

    def draw_entities(self):
        """Draws all entities on the map."""
        for entity in self.game_engine.game_logic.entities:
            if not entity.is_disposed():
                entity.draw(self.screen, self.game_engine.camera)

    def draw_entities_health_bars(self):
        """Draws health bars for all entities on the map."""
        for entity in self.game_engine.game_logic.entities:
            if not entity.is_disposed():
                entity.draw_health_bar(self.screen, self.game_engine.camera)

    def update_enemies(self):
        """Updates all enemies' behavior."""
        for entity in self.game_engine.game_logic.entities:
            if not entity.is_disposed() and isinstance(entity, Enemy):
                entity.update()

    def update(self, attack_direction: AttackDirection = None):
        """Updates the map engine state."""
        if not self.initialized:
            raise RuntimeError("Game engine not initialized.")

        # Handle attack input and timer
        if attack_direction is not None and attack_direction != AttackDirection.NONE:
            self.current_attack_direction = attack_direction
            self.attack_timer = statics.ATTACK_DURATION_FRAMES
            # Clear the damaged entities set for the new attack
            self.damaged_entities_this_attack.clear()
        
        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.current_attack_direction = AttackDirection.NONE
                # Clear damaged entities when attack ends
                self.damaged_entities_this_attack.clear()

        if self.game_engine.player and not self.game_engine.is_map_editor:
            # Center camera on player (player position is already in pixels)
            self.game_engine.camera.x = self.game_engine.player.x - self.screen.get_width() // 2
            self.game_engine.camera.y = self.game_engine.player.y - self.screen.get_height() // 2

        self.draw_map()
        self.draw_game_starting_position()
        # self.draw_player()
        self.draw_entities()
        self.update_enemies()
        self.game_engine.player.update()  # Update player state including invincibility timer
        self.game_engine.game_logic.pickup_coin(self.game_engine.player)
        self.game_engine.game_logic.deal_damage(
            self.game_engine.player, 
            self.current_attack_direction, 
            self.attack_timer, 
            self.damaged_entities_this_attack
        )
        self.draw_entities_health_bars()

        self.draw_camera()
        
        # Draw attack if timer is active
        if self.attack_timer > 0:
            self.draw_attack(self.current_attack_direction)
        
        # Draw UI (inventory, etc.)
        if not self.game_engine.is_map_editor:
            self.game_engine.player.inventory.draw(self.screen, self.game_engine.player)
        
        # Clean up disposed entities
        self.game_engine.game_logic.cleanup_disposed_entities()
            
        pygame.display.flip()



    def print_map(self):
        """Prints the generated map to console."""
        if self.map_data:
            for row in self.map_data:
                row_str = ' '.join(str(tile) for tile in row)
                print(row_str)
        else:
            print("No map data available to print.")


class Inventory(UI):
    def __init__(self):
        super().__init__()
        self.items = []

    def __add__(self, item):
        """Adds an item to the inventory."""
        self.items.append(item)

    def append(self, item):
        """Appends an item to the inventory."""
        self.items.append(item)

    def clear(self):
        """Clears the inventory."""
        self.items.clear()

    def __len__(self):
        """Returns the number of items in the inventory."""
        return len(self.items)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def draw(self, screen, player):
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

    def update(self):
        super().update()
        # Update inventory items
        for item in self.items:
            item.update()
            


class Player(Entity):
    def __init__(self, game_engine:GameEngine, starting_pos=statics.PLAYER_STARTING_POSITION, name="Player", size=statics.PLAYER_SIZE):
        # Ensure player starts at the center of the starting tile
        tile_size = statics.TILE_SIZE
        centered_pos = (starting_pos[0] + tile_size // 2, starting_pos[1] + tile_size // 2)
        super().__init__(name=name, starting_pos=centered_pos, entity_type=EntityType.PLAYER, size=size)
        self.game_engine = game_engine
        self.inventory = Inventory()
        self.invincibility_timer = 0  # Invincibility timer to prevent immediate damage after reset

    def update(self):
        """Update the player state, including invincibility timer."""
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

    def move(self, dx, dy):
        """Moves the player by dx and dy."""
        tile_size = statics.TILE_SIZE
        
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy

        # Check map boundaries (considering player is positioned at tile centers)
        if new_x - tile_size // 2 < 0 or new_x + tile_size // 2 >= statics.MAP_WIDTH * tile_size:
            return
        if new_y - tile_size // 2 < 0 or new_y + tile_size // 2 >= statics.MAP_HEIGHT * tile_size:
            return

        if self.game_engine.map_engine.map_data:
            # Calculate which tile the player center would be in
            tile_x = new_x // tile_size
            tile_y = new_y // tile_size

            if 0 <= tile_x < len(self.game_engine.map_engine.map_data[0]) and 0 <= tile_y < len(self.game_engine.map_engine.map_data):
                tile_type = self.game_engine.map_engine.map_data[tile_y][tile_x]
                if tile_type == 1:  # water
                    return
        self.x = new_x
        self.y = new_y

    def reset(self):
        """Resets the player position and health."""
        tile_size = statics.TILE_SIZE
        # Position player at the center of the starting tile
        self.x = statics.PLAYER_STARTING_POSITION[0] + tile_size // 2
        self.y = statics.PLAYER_STARTING_POSITION[1] + tile_size // 2
        self.health = 100
        self.inventory = Inventory()
        self.entity_type = EntityType.PLAYER  # Ensure entity type is set correctly
        self.invincibility_timer = 60  # 1 second of invincibility at 60 FPS


class Enemy(Entity):
    def __init__(self, game_engine: GameEngine, starting_pos=statics.ENEMY_STARTING_POSITION, name="Enemy", size=statics.ENEMY_SIZE):
        super().__init__(name=name, starting_pos=starting_pos, entity_type=EntityType.ENEMY, size=size)
        self.game_engine = game_engine
        self.speed = statics.ENEMY_SPEED  # Speed of the enemy movement
        self.damage_cooldown = 0  # Cooldown timer for dealing damage

    def update(self):
        """Updates the enemy's behavior."""
        if self.is_disposed():
            return
        
        # Update damage cooldown timer
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        # Simple AI: move towards the player if within a certain distance
        player = self.game_engine.player
        if player.is_disposed():
            return
        
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx**2 + dy**2)**0.5

        if distance < statics.ENEMY_AGGRO_RADIUS and distance > 0:
            # Normalize direction vector
            dx_normalized = dx / distance
            dy_normalized = dy / distance
            
            # Calculate new position
            new_x = self.x + dx_normalized * self.speed
            new_y = self.y + dy_normalized * self.speed

            # Check map boundaries
            tile_size = statics.TILE_SIZE
            if (new_x - self.size // 2 >= 0 and 
                new_x + self.size // 2 < len(self.game_engine.map_engine.map_data[0]) * tile_size and
                new_y - self.size // 2 >= 0 and 
                new_y + self.size // 2 < len(self.game_engine.map_engine.map_data) * tile_size):
                
                # Check for water collision
                tile_x = int(new_x // tile_size)
                tile_y = int(new_y // tile_size)
                
                if (0 <= tile_x < len(self.game_engine.map_engine.map_data[0]) and 
                    0 <= tile_y < len(self.game_engine.map_engine.map_data)):
                    tile_type = self.game_engine.map_engine.map_data[tile_y][tile_x]
                    if tile_type != 1:  # Not water
                        # Update position
                        self.x = new_x
                        self.y = new_y
            
            # Check for collision with player (only deal damage if cooldown is 0 and player is not invincible)
            if distance < self.size and self.damage_cooldown <= 0 and player.invincibility_timer <= 0:
                player.health -= statics.ENEMY_DAMAGE
                # Set damage cooldown to prevent continuous damage
                self.damage_cooldown = statics.ATTACK_DURATION_FRAMES
                if player.health <= 0:
                    player.dispose()

class Camera:
    def __init__(self, display_camera_location=False):
        self.x = 0
        self.y = 0
        self.display_camera_location = display_camera_location

    def move(self, dx, dy):
        """Moves the camera by dx and dy."""
        self.x += dx
        self.y += dy

    def reset(self):
        """Resets the camera position to the top-left corner."""
        self.x = 0
        self.y = 0


