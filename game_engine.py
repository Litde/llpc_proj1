import random
import statics


class GameEngine:
    def __init__(self):
        self.map_engine = MapEngine()


class MapEngine:
    def __init__(self, map_path=None):
        self.map_data = self.load_map(map_path) if map_path else None
        self.seed = None
        self.width = 20
        self.height = 20

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
        with open(f"{statics.MAPS_ROOT}/name", 'w') as f:
            for row in self.map_data:
                f.write(' '.join(str(tile) for tile in row) + '\n')

    def load_map(self, map_path: str) -> None:
        """Loads a map from a specified file path."""
        pass

    def get_tile_symbol(self, tile_type):
        """Returns a symbol for display purposes."""
        symbols = {0: '🌱', 1: '🌊', 2: '⛰️', 3: '🌲'}
        return symbols.get(tile_type, '?')

    def print_map(self):
        """Prints the generated map to console."""
        if self.map_data:
            for row in self.map_data:
                print(''.join(self.get_tile_symbol(tile) for tile in row))