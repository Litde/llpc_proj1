import random
import statics
import pygame


class GameEngine:
    def __init__(self):
        self.map_engine = None
        self.camera = None
        self.screen = None
        self.clock = None
        self.initialized = False
        self.player = None

        self.reset()

    def initialize_screen(self, width=800, height=600) -> None:
        """Initializes the game screen with given dimensions."""
        if self.initialized:
            return
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Game Engine")
        self.clock = pygame.time.Clock()
        self.clock.tick(statics.FPS)

    def initialize_map_engine(self, map_path=None) -> None:
        """Initializes the map engine with an optional map path."""
        if self.map_engine is not None:
            return
        self.camera = Camera(display_camera_location=False)
        self.map_engine = MapEngine(self.screen, self.camera, self.player, game_engine_initalized=True, map_path=map_path)
        self.initialized = True

    def initialize_player(self, name="Player") -> None:
        """Initializes the player with a given name."""
        self.player = Player(name=name)
        self.player.x = 0
        self.player.y = 0
        self.player.health = 100
        self.player.inventory = []

    def reset(self):
        """Resets the game engine to its initial state."""
        self.map_engine = None
        self.camera = None
        self.screen = None
        self.clock = None
        self.initialized = False
        self.initialize_player()
        self.initialize_screen()
        self.initialize_map_engine()



class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.x = 0
        self.y = 0
        self.health = 100
        self.inventory = []

    def move(self, dx, dy):
        """Moves the player by dx and dy."""
        self.x += dx
        self.y += dy


class Camera:
    def __init__(self, display_camera_location=False):
        self.x = 0
        self.y = 0

    def move(self, dx, dy):
        """Moves the camera by dx and dy."""
        self.x += dx
        self.y += dy

    def reset(self):
        """Resets the camera position to the top-left corner."""
        self.x = 0
        self.y = 0


class MapEngine:
    def __init__(self, screen, camera: Camera, player: Player, game_engine_initalized=False, map_path=None):
        self.map_data = self.load_map(map_path) if map_path else None
        self.seed = None
        self.width = 20
        self.height = 20
        self.game_engine_initialized = game_engine_initalized
        self.screen = screen
        self.camera = camera
        self.player = player


    def generate_seeded_map(self, seed=None, width=20, height=20):
        """Generates a map based on a seeded random number generator."""
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
        """Generates a map based on a non-seeded random number generator."""
        return self.generate_seeded_map(seed=None, width=width, height=height)

    def save_map(self, name="random_map") -> None:
        """Saves the current map to a specified file path."""
        with open(f"{statics.MAPS_ROOT}/{name}", 'w') as f:
            for row in self.map_data:
                f.write(' '.join(str(tile) for tile in row) + '\n')

    def load_map(self, map_path: str) -> None:
        """Loads a map from a specified file path."""
        pass

    def get_tile_symbol(self, tile_type):
        """Returns a symbol for display purposes."""
        symbols = {0: '🌱', 1: '🌊', 2: '⛰️', 3: '🌲'}
        return symbols.get(tile_type, '?')

    def display_map(self):
        if not self.game_engine_initialized:
            raise RuntimeError("Game engine not initialized.")

        if self.map_data is None:
            raise ValueError("No map data available to display.")

        # Clear screen using class field
        self.screen.fill((0, 0, 0))  # Black background

        # Define colors for different tile types
        tile_colors = {
            0: (50, 150, 50),  # grass - green
            1: (50, 50, 150),  # water - blue
            2: (100, 100, 100),  # mountain - gray
            3: (0, 100, 0)  # forest - dark green
        }

        # Calculate visible area using class fields
        screen_width, screen_height = self.screen.get_size()
        tiles_x = screen_width // statics.TILE_SIZE + 2
        tiles_y = screen_height // statics.TILE_SIZE + 2

        start_x = max(0, self.camera.x // statics.TILE_SIZE)
        start_y = max(0, self.camera.y // statics.TILE_SIZE)
        end_x = min(self.width, start_x + tiles_x)
        end_y = min(self.height, start_y + tiles_y)

        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if y < len(self.map_data) and x < len(self.map_data[y]):
                    tile = self.map_data[y][x]
                    color = tile_colors.get(tile, (255, 0, 255))  # Default magenta

                    # Calculate screen position
                    screen_x = x * statics.TILE_SIZE - self.camera.x
                    screen_y = y * statics.TILE_SIZE - self.camera.y

                    # Draw tile rectangle
                    pygame.draw.rect(self.screen, color,
                                     (screen_x, screen_y, statics.TILE_SIZE, statics.TILE_SIZE))

                    # Draw border for better visibility
                    # pygame.draw.rect(self.screen, (255, 255, 255),
                    #                  (screen_x, screen_y, statics.TILE_SIZE, statics.TILE_SIZE), 1)

    def draw_player(self):
        """Draws the player on the map."""
        if self.game_engine_initialized and self.player:
            player_color = (255, 0, 0)
            player_size = 20
            player_x = self.player.x * statics.TILE_SIZE - self.camera.x + statics.TILE_SIZE // 2
            player_y = self.player.y * statics.TILE_SIZE - self.camera.y + statics.TILE_SIZE // 2
            pygame.draw.circle(self.screen, player_color, (int(player_x), int(player_y)), player_size)


    def update(self):
        """Updates the map engine state."""
        if not self.game_engine_initialized:
            raise RuntimeError("Game engine not initialized.")

        # Update camera position based on player position
        if self.player:
            self.camera.x = self.player.x * statics.TILE_SIZE - self.screen.get_width() // 2
            self.camera.y = self.player.y * statics.TILE_SIZE - self.screen.get_height() // 2

        # Draw the map and player
        self.display_map()
        self.draw_player()
        pygame.display.flip()



    def print_map(self):
        """Prints the generated map to console."""
        if self.map_data:
            for row in self.map_data:
                print(''.join(self.get_tile_symbol(tile) for tile in row))