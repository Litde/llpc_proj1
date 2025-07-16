import pygame
import sys
import os

# Add parent directory to path to import from parent package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces import AttackDirection
from game_engine import GameEngine
import statics
from map_editor import MapEditor

map_name = "random_map.txt"

def main():

    game_engine = GameEngine(is_map_editor=True, display_camera_location=True)
    game_engine.initialize()

    map_editor = MapEditor(game_engine)

    game_engine.map_engine.initialize(windows_size=(1920, 1080))

    if not game_engine.initialized:
        raise Exception("Game engine not initialized. Call initialize() first.")
    
    # Load a predefined map (adjust path for map editor)
    import os
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    game_engine.map_engine.load_map(map_name)

    running = True
    selected_tile = None

    while running:
        attack = AttackDirection.NONE
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    game_engine.camera.move(-statics.TILE_SIZE, 0)
                elif event.key == pygame.K_RIGHT:
                    game_engine.camera.move(statics.TILE_SIZE, 0)
                elif event.key == pygame.K_UP:
                    game_engine.camera.move(0, -statics.TILE_SIZE)
                elif event.key == pygame.K_DOWN:
                    game_engine.camera.move(0, statics.TILE_SIZE)
                elif event.key == pygame.K_0:
                    selected_tile = 0
                elif event.key == pygame.K_1:
                    selected_tile = 1
                elif event.key == pygame.K_2:
                    selected_tile = 2
                elif event.key == pygame.K_3:
                    selected_tile = 3
                elif ctrls := pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if event.key == pygame.K_s:
                        # Save the current map
                        game_engine.map_engine.save_map(map_name)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    tile_x = (mouse_x + game_engine.camera.x) // statics.TILE_SIZE
                    tile_y = (mouse_y + game_engine.camera.y) // statics.TILE_SIZE
                    if selected_tile is not None:
                        map_editor.change_tile(tile_x, tile_y, selected_tile)

        game_engine.map_engine.update()

        
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()