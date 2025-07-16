import pygame
import statics
from game_engine import GameEngine
from interfaces import EntityType, AttackDirection


def main():
    game_engine = GameEngine()

    game_engine.initialize()
    game_engine.map_engine.initialize(windows_size=(1920, 1080))

    if not game_engine.initialized:
        raise Exception("Game engine not initialized. Call initialize() first.")

    # game_engine.map_engine.generate_random_map(width=250, height=250)
    # game_engine.map_engine.save_map("test_map.txt")
    game_engine.map_engine.load_map("test_map.txt")

    game_engine.game_logic.populate_entities(num_entities=1000, entity_type=EntityType.ITEM, size=statics.COIN_SIZE)

    game_engine.game_logic.populate_entities(num_entities=1000, entity_type=EntityType.ENEMY, size=statics.ENEMY_SIZE, health=100)

    game_engine.game_logic.populate_entities(num_entities=100, entity_type=EntityType.HEALTH, size=statics.ENEMY_SIZE)


    # game_engine.map_engine.print_map()

    running = True
    while running:
        attack = AttackDirection.NONE
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Z + Arrow keys for double speed movement
                elif keys[pygame.K_z] and event.key == pygame.K_RIGHT:
                    game_engine.player.move(statics.PLAYER_SPEED * 2, 0)
                elif keys[pygame.K_z] and event.key == pygame.K_LEFT:
                    game_engine.player.move(-statics.PLAYER_SPEED * 2, 0)
                elif keys[pygame.K_z] and event.key == pygame.K_UP:
                    game_engine.player.move(0, -statics.PLAYER_SPEED * 2)
                elif keys[pygame.K_z] and event.key == pygame.K_DOWN:
                    game_engine.player.move(0, statics.PLAYER_SPEED * 2)
                # X + Arrow keys for attacks
                elif keys[pygame.K_x] and event.key == pygame.K_RIGHT:
                    attack = AttackDirection.RIGHT
                elif keys[pygame.K_x] and event.key == pygame.K_LEFT:
                    attack = AttackDirection.LEFT
                elif keys[pygame.K_x] and event.key == pygame.K_UP:
                    attack = AttackDirection.UP
                elif keys[pygame.K_x] and event.key == pygame.K_DOWN:
                    attack = AttackDirection.DOWN
                elif event.key == pygame.K_LEFT:
                    game_engine.player.move(-statics.PLAYER_SPEED, 0)
                elif event.key == pygame.K_RIGHT:
                    game_engine.player.move(statics.PLAYER_SPEED, 0)
                elif event.key == pygame.K_UP:
                    game_engine.player.move(0, -statics.PLAYER_SPEED)
                elif event.key == pygame.K_DOWN:
                    game_engine.player.move(0, statics.PLAYER_SPEED)
                elif event.key == pygame.K_r:
                    game_engine.reset_player()
                elif event.key == pygame.K_i:
                    game_engine.player.inventory.toggle_inventory()

        game_engine.map_engine.update(attack_direction=attack)


    pygame.quit()



if __name__ == '__main__':
    main()