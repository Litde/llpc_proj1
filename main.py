import pygame
from game_engine import GameEngine


def main():
    game_engine = GameEngine()

    game_engine.map_engine.generate_random_map(height=20, width=100)
    game_engine.map_engine.save_map("generated_map_pozioma.txt")
    game_engine.map_engine.load_map("generated_map_pozioma.txt")

    # Game loop to keep window open
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Display map
        game_engine.map_engine.display_map()

        # Control frame rate
        game_engine.clock.tick(60)

    pygame.quit()



if __name__ == '__main__':
    main()