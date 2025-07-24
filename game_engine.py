from dataclasses import dataclass
import random
from typing import List, Optional
import statics
import pygame
import pygame, os
from interfaces import AttackDirection, EntityType,WeaponType, Entity, UI

os.environ['SDL_VIDEO_CENTERED'] = '1'





class GameEngine:
    def __init__(self, is_map_editor:bool = False, display_camera_location:bool = False):
        self.game_logic = GameLogic(self)
        self.player = Player(self)
        self.camera = Camera(display_camera_location=display_camera_location)
        self.map_engine = MapEngine(self)
        self.weapons_list: dict[WeaponType, Weapon] = {}
        self.is_map_editor = is_map_editor
        self.initialized = False

        
        pygame.init()
        pygame.display.set_caption("LLPC Project 1")
        
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

    def __calculate_level_based_on_player_distance(self, entity_position: tuple[int, int], num_levels: int = 6) -> int:
        player_pos = self.game_engine.player.get_position()
        entity_pos = entity_position

        # Calculate Euclidean distance between player and entity
        distance = ((player_pos[0] - entity_pos[0]) ** 2 + (player_pos[1] - entity_pos[1]) ** 2) ** 0.5

        # Universal scaling: map max distance to levels
        # Estimate max possible distance based on map size
        map_engine = self.game_engine.map_engine
        if map_engine.map_data:
            map_width = len(map_engine.map_data[0]) * statics.TILE_SIZE
            map_height = len(map_engine.map_data) * statics.TILE_SIZE
        else:
            map_width = statics.MAP_WIDTH
            map_height = statics.MAP_HEIGHT
        max_distance = ((map_width) ** 2 + (map_height) ** 2) ** 0.5

        # Clamp distance to [0, max_distance]
        distance = max(0, min(distance, max_distance))
        # Calculate level: 1 (closest) to num_levels (farthest)
        level = int((distance / max_distance) * (num_levels - 1)) + 1
        return level

    def create_entity(self, name: str = "Entity", entity_type: EntityType = EntityType.NPC, starting_pos: tuple = (0, 0), size: int = statics.TILE_SIZE, health: int = 100):
        """Creates a new entity with the given parameters."""
        if entity_type == EntityType.ENEMY:
            level = self.__calculate_level_based_on_player_distance(starting_pos)
            entity = Enemy(self.game_engine, name=name, starting_pos=starting_pos, size=size, level=level, health=health)
            entity.health = health
            

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

        tile_x = map_width_pixels // statics.TILE_SIZE
        tile_y = map_height_pixels // statics.TILE_SIZE
        
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
        """Handles picking up a coin or healing entity."""
        for entity in self.entities[:]:
            if not entity.is_disposed():
                if entity.entity_type == EntityType.ITEM:
                    if player.check_collision(entity):
                        self.entities.remove(entity)
                        player.coins += 1
                        entity.dispose()
                elif entity.entity_type == EntityType.HEALTH:
                    if player.check_collision(entity):
                        self.entities.remove(entity)
                        player.health = min(player.health + 20, 100)
                        entity.dispose()

    def add_experience_to_player(self, exp: int):
        if self.game_engine.player.level+1 in self.game_engine.player.required_exp:
            required_exp = self.game_engine.player.required_exp[self.game_engine.player.level+1]
            if self.game_engine.player.experience + exp >= required_exp:
                rest = self.game_engine.player.experience + exp - required_exp
                self.game_engine.player.level_up()
                self.game_engine.player.experience = rest
            else:
                self.game_engine.player.experience += exp

    def deal_damage(self, player, attack_direction, attack_timer, damaged_entities_this_attack, damage=statics.ATTACK_DAMAGE):
        """Deals damage to entities in the attack area based on the player's weapon's attack pattern. Only damages entities whose center is inside the attack cell."""
        if player.is_disposed() or attack_timer <= 0:
            return

        weapon = getattr(player, 'weapon', None)
        if not weapon or not weapon.attack_pattern:
            return

        damage_out = weapon.damage * player.level if hasattr(weapon, 'damage') else damage * player.level

        tile_size = statics.TILE_SIZE
        player_tile_x = player.x // tile_size
        player_tile_y = player.y // tile_size
        player_center_x = player_tile_x * tile_size + tile_size // 2
        player_center_y = player_tile_y * tile_size + tile_size // 2

        # For each cell in the attack pattern, check for entity center inside attack cell
        for dx, dy in weapon.attack_pattern.pattern_data:
            # Rotate pattern based on attack_direction (same as draw_attack)
            if attack_direction == AttackDirection.UP:
                rel_dx, rel_dy = dx, -dy
            elif attack_direction == AttackDirection.DOWN:
                rel_dx, rel_dy = dx, dy
            elif attack_direction == AttackDirection.LEFT:
                rel_dx, rel_dy = -dy, dx
            elif attack_direction == AttackDirection.RIGHT:
                rel_dx, rel_dy = dy, -dx
            else:
                rel_dx, rel_dy = dx, dy

            # Calculate the center of the attack cell in world coordinates
            cell_center_x = player_center_x + rel_dx * tile_size
            cell_center_y = player_center_y + rel_dy * tile_size

            # Create a rect for the attack cell
            attack_cell_rect = pygame.Rect(
                cell_center_x - tile_size // 2,
                cell_center_y - tile_size // 2,
                tile_size,
                tile_size
            )

            for entity in self.entities:
                if (not entity.is_disposed() and 
                    entity.entity_type != EntityType.PLAYER and 
                    entity.entity_type != EntityType.ITEM and
                    entity not in damaged_entities_this_attack):

                    # Use entity center for strictness
                    entity_center_x = entity.x
                    entity_center_y = entity.y

                    if attack_cell_rect.collidepoint(entity_center_x, entity_center_y):
                        damaged_entities_this_attack.add(entity)
                        entity.health -= damage_out
                        if entity.health <= 0:
                            if entity.entity_type == EntityType.ENEMY:
                                self.add_experience_to_player(entity.exp_reward)
                            self.dispose_entity(entity)
                        


class MapEngine:
    def __init__(self, game_engine: GameEngine, map_path:Optional[str] = None):
        self.map_data: Optional[List[List[int]]] = None
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
        if not self.initialized or not self.screen:
            raise RuntimeError("Screen not initialized. Call initialize() first.")

        screen_width, screen_height = self.screen.get_size()
        tile_size = statics.TILE_SIZE

        width = screen_width // tile_size
        height = screen_height // tile_size

        return self.generate_seeded_map(seed=None, width=width, height=height)

    def save_map(self, name="random_map") -> None:
        if self.map_data is None:
            raise ValueError("No map data available to save.")
        with open(f"{statics.MAPS_ROOT}/{name}", 'w') as f:
            for row in self.map_data:
                if isinstance(row, int):
                    f.write(str(row) + '\n')
                else:
                    f.write(' '.join(str(tile) for tile in row) + '\n')

    def load_map(self, map_path: str) -> tuple[int, int]:
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
    
    def change_tile(self, tile_x: int, tile_y: int, new_tile_type: int):
        """
        Change the tile at the specified coordinates to a new tile type.
        """
        if not self.map_data:
            raise ValueError("No map data available to change tiles.")
        
        if tile_y < 0 or tile_y >= len(self.map_data) or tile_x < 0 or tile_x >= len(self.map_data[0]):
            raise IndexError("Tile coordinates out of bounds.")
        
        # Convert new_tile_type to integer
        try:
            new_tile_type = new_tile_type
        except ValueError:
            raise ValueError("Invalid tile type. Must be an integer.")

        self.map_data[tile_y][tile_x] = new_tile_type

    def is_tile_occupied(self, tile_x: int, tile_y: int) -> bool:
        """
        Check if a tile at the specified coordinates is occupied by an entity.
        """
        if not self.game_engine or not self.game_engine.game_logic or self.map_data is None:
            return False

        for entity in self.game_engine.game_logic.entities:
            if (entity.x // statics.TILE_SIZE == tile_x and 
                entity.y // statics.TILE_SIZE == tile_y and 
                not entity.is_disposed()) and self.map_data[tile_y][tile_x] == statics.TILE_VALUES[1]:
                return True
        return False

    def draw_map(self):
        if self.map_data is None or not self.screen:
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
        if self.screen is None:
            return
        if self.game_engine.initialized and self.game_engine.camera.display_camera_location:
            camera_color = (255, 255, 0)
            # Draw camera border around the screen edges to show the viewport
            pygame.draw.rect(self.screen, camera_color, 
                           (0, 0, self.screen.get_width(), self.screen.get_height()), 2)

    def draw_game_starting_position(self):
        """Draws the game starting position on the map."""
        if self.screen is None:
            return
        
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
        """Draws the attack area for attack_duration frames after an attack is triggered, and only allows a new attack after attack_cooldown reaches 0."""
        if self.screen is None:
            return

        weapon = self.game_engine.player.weapon
        if not weapon or not weapon.attack_pattern:
            return

        # Draw attack area if attack_timer > 0 (attack is active)
        if not hasattr(weapon, 'attack_timer') or weapon.attack_timer <= 0:
            return

        if self.game_engine.initialized and self.game_engine.player:
            attack_color = statics.ATTACK_COLOR
            tile_size = statics.TILE_SIZE
            # Calculate which tile the player is currently in (same as draw_player)
            tile_x = self.game_engine.player.x // tile_size
            tile_y = self.game_engine.player.y // tile_size
            # Calculate the center of that tile in world coordinates
            tile_center_x = tile_x * tile_size + tile_size // 2
            tile_center_y = tile_y * tile_size + tile_size // 2
            # Calculate screen position relative to camera
            screen_center_x = tile_center_x - self.game_engine.camera.x
            screen_center_y = tile_center_y - self.game_engine.camera.y

            # Draw each attack cell in the pattern relative to the player
            for dx, dy in weapon.attack_pattern.pattern_data:
                # Rotate pattern based on attack_direction
                if attack_direction == AttackDirection.UP:
                    rel_dx, rel_dy = dx, -dy
                elif attack_direction == AttackDirection.DOWN:
                    rel_dx, rel_dy = dx, dy
                elif attack_direction == AttackDirection.LEFT:
                    rel_dx, rel_dy = -dy, dx
                elif attack_direction == AttackDirection.RIGHT:
                    rel_dx, rel_dy = dy, -dx
                else:
                    rel_dx, rel_dy = dx, dy

                cell_x = screen_center_x + rel_dx * tile_size
                cell_y = screen_center_y + rel_dy * tile_size
                pygame.draw.rect(
                    self.screen,
                    attack_color,
                    (cell_x - tile_size // 2, cell_y - tile_size // 2, tile_size, tile_size),
                    2
                )

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

    def update(self, attack_direction: AttackDirection = AttackDirection.NONE):
        """Updates the map engine state."""
        if not self.initialized or self.screen is None:
            raise RuntimeError("Game engine not initialized.")

        weapon = self.game_engine.player.weapon
        # Handle attack input and timers for weapon
        if weapon:
            # Decrement timers
            if weapon.attack_timer > 0:
                weapon.attack_timer -= 1
            if weapon.cooldown_timer > 0:
                weapon.cooldown_timer -= 1

            # Handle attack input
            if attack_direction is not None and attack_direction != AttackDirection.NONE:
                if weapon.cooldown_timer <= 0:
                    self.current_attack_direction = attack_direction
                    weapon.attack_timer = weapon.attack_duration
                    weapon.cooldown_timer = weapon.attack_cooldown
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
        # Use weapon's attack_timer for damage
        attack_timer = weapon.attack_timer if weapon else 0
        self.game_engine.game_logic.deal_damage(
            self.game_engine.player, 
            self.current_attack_direction, 
            attack_timer, 
            self.damaged_entities_this_attack
        )
        self.draw_entities_health_bars()

        self.draw_camera()

        # Draw attack if timer is active (use weapon's attack_timer)
        if weapon and weapon.attack_timer > 0:
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

    def draw(self, screen, player=None):
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
        
        # Draw title and experience bar/text beside it
        title_text = font.render("Inventory", True, (255, 255, 255))
        title_x = self.inventory_x + 5
        title_y = self.inventory_y + 5
        screen.blit(title_text, (title_x, title_y))

        if hasattr(player, 'experience') and hasattr(player, 'level'):
            exp = player.experience
            level = player.level
            required_exp = player.required_exp.get(level + 1, 100)
            exp_text = font.render(f"EXP: {exp} / {required_exp}", True, (0, 191, 255))
            exp_text_x = title_x + title_text.get_width() + 20
            exp_text_y = title_y
            screen.blit(exp_text, (exp_text_x, exp_text_y))
            # Draw small experience bar beside exp text
            exp_bar_width = 80
            exp_bar_height = 10
            exp_bar_x = exp_text_x + exp_text.get_width() + 10
            exp_bar_y = exp_text_y + (title_text.get_height() - exp_bar_height) // 2
            exp_ratio = min(exp / required_exp, 1.0)
            pygame.draw.rect(screen, (40, 40, 40), (exp_bar_x, exp_bar_y, exp_bar_width, exp_bar_height))
            pygame.draw.rect(screen, (0, 128, 255), (exp_bar_x, exp_bar_y, int(exp_bar_width * exp_ratio), exp_bar_height))
        
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
        
        # Draw items count and coins count beside each other, top right
        items_count = len(inventory_items)
        coins_count = getattr(player, 'coins', 0)
        count_text = font.render(f"Items: {items_count}", True, (255, 255, 255))
        coin_text = font.render(f"Coins: {coins_count}", True, (255, 223, 0))
        # Calculate widths for proper alignment
        total_width = count_text.get_width() + 12 + coin_text.get_width()
        start_x = self.inventory_x + inventory_width - total_width - 10
        y = self.inventory_y + 5
        screen.blit(count_text, (start_x, y))
        screen.blit(coin_text, (start_x + count_text.get_width() + 12, y))

    def update(self):
        super().update()
        # Update inventory items
        for item in self.items:
            item.update()
            

@dataclass
class AttackPattern:
    pattern_type: str
    pattern_data: list[tuple[int, int]]  

@dataclass
class Weapon:
    name: str
    weapon_type: WeaponType
    damage: int
    attack_pattern: AttackPattern
    attack_cooldown: int
    attack_duration: int = statics.ATTACK_DURATION_FRAMES
    attack_timer: int = 0
    cooldown_timer: int = 0

    def __hash__(self) -> int:
        return hash((self.name, self.weapon_type, self.damage, self.attack_pattern, self.attack_cooldown, self.attack_duration))



class Player(Entity):
    def __init__(self, game_engine:GameEngine, starting_pos=statics.PLAYER_STARTING_POSITION, name="Player", size=statics.PLAYER_SIZE):
        tile_size = statics.TILE_SIZE
        centered_pos = (starting_pos[0] + tile_size // 2, starting_pos[1] + tile_size // 2)
        super().__init__(name=name, starting_pos=centered_pos, entity_type=EntityType.PLAYER, size=size)
        self.game_engine = game_engine
        self.inventory = Inventory()
        self.coins = 0
        self.invincibility_timer = 0
        self.experience = 0
        self.required_exp = {
            2: 100,
            3: 200,
            4: 300,
            5: 500,
            6: 800,
        }
        self.weapon: Optional[Weapon] = None

    def add_weapon(self, weapon: Weapon):
        """Adds a weapon to the player."""
        if not isinstance(weapon, Weapon):
            raise TypeError("Expected a Weapon instance.")
        self.weapon = weapon

    def update(self):
        """Update the player state, including invincibility timer."""
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

    def move(self, dx, dy):
        """Moves the player by dx and dy."""
        tile_size = statics.TILE_SIZE
        
        new_x = self.x + dx
        new_y = self.y + dy

        if new_x - tile_size // 2 < 0 or new_x + tile_size // 2 >= statics.MAP_WIDTH * tile_size:
            return
        if new_y - tile_size // 2 < 0 or new_y + tile_size // 2 >= statics.MAP_HEIGHT * tile_size:
            return

        if self.game_engine.map_engine.map_data:
            tile_x = new_x // tile_size
            tile_y = new_y // tile_size

            if 0 <= tile_x < len(self.game_engine.map_engine.map_data[0]) and 0 <= tile_y < len(self.game_engine.map_engine.map_data):
                tile_type = self.game_engine.map_engine.map_data[tile_y][tile_x]
                if tile_type == 1:
                    return

        self.x = new_x
        self.y = new_y

    def level_up(self):
        """Levels up the player and increases health."""
        self.level += 1
        self.health += 20

    def reset(self):
        """Resets the player position and health."""
        tile_size = statics.TILE_SIZE
        self.x = statics.PLAYER_STARTING_POSITION[0] + tile_size // 2
        self.y = statics.PLAYER_STARTING_POSITION[1] + tile_size // 2
        self.health = 100
        self.inventory = Inventory()
        self.entity_type = EntityType.PLAYER  
        self.invincibility_timer = 60  
        self.experience = 0
        self.required_exp = {
            2: 100,
            3: 200,
            4: 300,
            5: 500,
            6: 800,
        }
        self.level = 1


class Enemy(Entity):
    def __init__(self, game_engine: GameEngine, starting_pos=statics.ENEMY_STARTING_POSITION, name="Enemy", size=statics.ENEMY_SIZE, level: int=1, health: int=100):
        super().__init__(name=name, starting_pos=starting_pos, entity_type=EntityType.ENEMY, size=size, health=health, level=level)
        self.game_engine = game_engine
        self.speed = statics.ENEMY_SPEED 
        self.damage_cooldown = 0
        self.exp_reward = level * 10

    def update(self):
        """Updates the enemy's behavior."""
        if not self.game_engine or not self.game_engine.game_logic or not self.game_engine.map_engine or not self.game_engine.map_engine.map_data:
            return
        if self.is_disposed():
            return
        
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        player = self.game_engine.player
        if player.is_disposed():
            return
        
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx**2 + dy**2)**0.5

        if distance < statics.ENEMY_AGGRO_RADIUS and distance > 0:
            dx_normalized = dx / distance
            dy_normalized = dy / distance
            
            new_x = self.x + dx_normalized * self.speed
            new_y = self.y + dy_normalized * self.speed
            
            tile_size = statics.TILE_SIZE
            if (new_x - self.size // 2 >= 0 and 
                new_x + self.size // 2 < len(self.game_engine.map_engine.map_data[0]) * tile_size and
                new_y - self.size // 2 >= 0 and 
                new_y + self.size // 2 < len(self.game_engine.map_engine.map_data) * tile_size):
                
                tile_x = int(new_x // tile_size)
                tile_y = int(new_y // tile_size)
                
                if (0 <= tile_x < len(self.game_engine.map_engine.map_data[0]) and 
                    0 <= tile_y < len(self.game_engine.map_engine.map_data)):
                    tile_type = self.game_engine.map_engine.map_data[tile_y][tile_x]
                    if tile_type != 1:
                        self.x = new_x
                        self.y = new_y
            
            if distance < self.size and self.damage_cooldown <= 0 and player.invincibility_timer <= 0:
                player.health -= statics.ENEMY_DAMAGE * self.level
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


