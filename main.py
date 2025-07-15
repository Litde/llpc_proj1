import pygame
import statics
from game_engine import GameEngine, AttackDirection


def main():
    game_engine = GameEngine()

    game_engine.initialize()
    game_engine.map_engine.initialize(windows_size=(1920, 1080))

    if not game_engine.initialized:
        raise Exception("Game engine not initialized. Call initialize() first.")

    # game_engine.map_engine.generate_random_map(width=3000, height=2000)
    # game_engine.map_engine.save_map("random_map.txt")
    game_engine.map_engine.load_map("random_map.txt")

    # game_engine.map_engine.print_map()

    running = True
    while running:
        attack = AttackDirection.NONE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif (event.mod & pygame.KMOD_SHIFT) and event.key == pygame.K_RIGHT:
                    game_engine.player.move(statics.PLAYER_SPEED * 2, 0)
                elif (event.mod & pygame.KMOD_SHIFT) and event.key == pygame.K_LEFT:
                    game_engine.player.move(-statics.PLAYER_SPEED * 2, 0)
                elif (event.mod & pygame.KMOD_SHIFT) and event.key == pygame.K_UP:
                    game_engine.player.move(0, -statics.PLAYER_SPEED * 2)
                elif (event.mod & pygame.KMOD_SHIFT) and event.key == pygame.K_DOWN:
                    game_engine.player.move(0, statics.PLAYER_SPEED * 2)
                # elif (event.mod & pygame.K_TAB) and event.key == pygame.K_RIGHT:
                #     attack = AttackDirection.RIGHT
                # elif (event.mod & pygame.K_TAB) and event.key == pygame.K_LEFT:
                #     attack = AttackDirection.LEFT
                # elif (event.mod & pygame.K_TAB) and event.key == pygame.K_UP:
                #     attack = AttackDirection.UP
                # elif (event.mod & pygame.K_TAB) and event.key == pygame.K_DOWN:
                #     attack = AttackDirection.DOWN
                elif event.key == pygame.K_LEFT:
                    game_engine.player.move(-statics.PLAYER_SPEED, 0)
                elif event.key == pygame.K_RIGHT:
                    game_engine.player.move(statics.PLAYER_SPEED, 0)
                elif event.key == pygame.K_UP:
                    game_engine.player.move(0, -statics.PLAYER_SPEED)
                elif event.key == pygame.K_DOWN:
                    game_engine.player.move(0, statics.PLAYER_SPEED)
                elif event.key == pygame.K_r:
                    game_engine.player.reset()

        game_engine.map_engine.update(attack_direction=attack)
        attack = AttackDirection.NONE


    pygame.quit()



if __name__ == '__main__':
    main()