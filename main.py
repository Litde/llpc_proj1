import pygame
from game_engine import GameEngine


def main():
    game_engine = GameEngine()

    game_engine.map_engine.generate_random_map(height=20, width=100)
    game_engine.map_engine.save_map("generated_map_pozioma.txt")
    game_engine.map_engine.load_map("generated_map_pozioma.txt")
    game_engine.map_engine.print_map()



if __name__ == '__main__':
    main()