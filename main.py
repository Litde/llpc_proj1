import pygame
from game_engine import GameEngine


def main():
    game_engine = GameEngine()

    game_engine.initialize()

    if not game_engine.initialized:
        raise Exception("Game engine not initialized. Call initialize() first.")

    game_engine.map_engine.generate_random_map()

    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        game_engine.map_engine.display_map()


    pygame.quit()



if __name__ == '__main__':
    main()