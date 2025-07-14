import pygame
import statics
from game_engine import GameEngine


def main():
    game_engine = GameEngine()

    game_engine.initialize()
    game_engine.map_engine.initialize(windows_size=(1920, 1080))

    if not game_engine.initialized:
        raise Exception("Game engine not initialized. Call initialize() first.")

    game_engine.map_engine.generate_map_in_proportions_of_screen()

    # game_engine.map_engine.print_map()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    game_engine.player.move(-statics.TILE_SIZE, 0)
                elif event.key == pygame.K_RIGHT:
                    game_engine.player.move(statics.TILE_SIZE, 0)
                elif event.key == pygame.K_UP:
                    game_engine.player.move(0, -statics.TILE_SIZE)
                elif event.key == pygame.K_DOWN:
                    game_engine.player.move(0, statics.TILE_SIZE)

        game_engine.map_engine.update()


    pygame.quit()



if __name__ == '__main__':
    main()