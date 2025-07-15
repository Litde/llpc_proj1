import random
import statics
import pygame
import pygame, os
os.environ['SDL_VIDEO_CENTERED'] = '1'


class GameEngine:
    def __init__(self):
        self.game_logic = GameLogic()
        self.player = Player(self)
        self.camera = Camera()
        self.map_engine = MapEngine(self)
        
        

        pygame.init()
        pygame.display.set_caption("Game Engine Example")
        
        self.initialized = False

        self.initialize()


    def initialize(self):
        self.player.reset()
        self.camera.reset()
        self.map_engine.initialize()
        self.initialized = True

    def reset(self):
        self.game_logic.reset()
        self.map_engine.reset()
        self.player.reset()
        self.camera.reset()
        self.initialized = False


class GameLogic:

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.fps = statics.FPS
        self.clock.tick(self.fps)

    def reset(self):
        self.clock = pygame.time.Clock()


class MapEngine:
    def __init__(self, game_engine: GameEngine, map_path:str=None):
        self.map_data = self.load_map(map_path) if map_path else None
        self.seed = None
        self.screen = None
        self.game_engine = game_engine
        self.initialized = False

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

    def draw_player(self):
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

    def update(self):
        """Updates the map engine state."""
        if not self.initialized:
            raise RuntimeError("Game engine not initialized.")

        if self.game_engine.player:
            # Center camera on player (player position is already in pixels)
            self.game_engine.camera.x = self.game_engine.player.x - self.screen.get_width() // 2
            self.game_engine.camera.y = self.game_engine.player.y - self.screen.get_height() // 2

        self.draw_map()
        self.draw_game_starting_position()
        self.draw_player()
        self.draw_camera()
        pygame.display.flip()



    def print_map(self):
        """Prints the generated map to console."""
        if self.map_data:
            for row in self.map_data:
                row_str = ' '.join(str(tile) for tile in row)
                print(row_str)
        else:
            print("No map data available to print.")



class Player:
    def __init__(self, game_engine:GameEngine, starting_pos=statics.PLAYER_STARTING_POSITION, name="Player"):
        self.game_engine = game_engine
        self.name = name
        self.x, self.y = starting_pos
        self.health = 100
        self.inventory = []

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
        self.inventory.clear()


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


