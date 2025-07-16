import pygame
import sys
import os
# Add parent directory to path to import from parent package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from interfaces import AttackDirection
from game_engine import GameEngine



class MapEditor:
    def __init__(self, game_engine: GameEngine):
        self.game_engine = game_engine

    def change_tile(self, tile_x: int, tile_y: int, new_tile_type: int) -> None:
        """
        Change the tile at the specified coordinates to a new tile type.
        """
        self.game_engine.map_engine.change_tile(tile_x, tile_y, new_tile_type)

