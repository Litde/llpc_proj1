# Game Engine Project

A tile-based 2D game engine built with Python and Pygame, featuring camera-based rendering, entity management, and attack systems.

## Project Structure

```
llpc_proj1/
├── README.md                # This file
├── main.py                  # Main game loop and input handling
├── game_engine.py          # Core game engine classes
├── interfaces.py           # Entity system and enums
├── statics.py             # Game constants and configuration
├── maps/                  # Map data files
│   └── random_map.txt     # Example map file
└── __pycache__/          # Python bytecode cache
```

## File Descriptions

### `main.py`
- **Purpose**: Entry point of the game
- **Features**:
  - Game initialization and main loop
  - Input handling (movement, attacks, combos)
  - Key combinations (Z+Arrow for fast movement, X+Arrow for attacks)
  - Entity population (spawns 1000 items on the map)

### `game_engine.py`
Core game engine containing multiple classes:

#### `GameEngine`
- Main orchestrator class
- Manages initialization and coordination between systems
- Contains references to all major subsystems

#### `GameLogic`
- Entity management system
- Creates and manages all game entities
- Handles entity population across the map
- Frame rate management

#### `MapEngine`
- Map rendering and management
- Camera-based tile culling (only draws visible tiles)
- Map generation (seeded and random)
- Map loading/saving functionality
- Attack visualization system
- Black border rendering beyond map boundaries

#### `Player`
- Inherits from Entity
- Movement with collision detection
- Tile-based positioning (centered in tiles)
- Water tile collision prevention
- Boundary checking

#### `Camera`
- Viewport management
- Follows player automatically
- Camera-relative coordinate calculations

### `interfaces.py`
- **Entity System**: Base Entity class with tile-centered rendering
- **Enums**: 
  - `AttackDirection` (UP, DOWN, LEFT, RIGHT, NONE)
  - `EntityType` (PLAYER, ENEMY, ITEM, NPC)
- **Camera Culling**: Only renders entities within camera view
- **Tile-Centered Drawing**: All entities snap to tile centers

### `statics.py`
Configuration constants:
- Map settings (tile size, dimensions)
- Player properties (size, speed, starting position)
- Attack settings (range, duration, colors)
- Entity colors and sizes
- Game performance settings (FPS)

## Key Features

### 🎮 Movement System
- **Arrow Keys**: Normal movement (1 tile per press)
- **Z + Arrow Keys**: Fast movement (2 tiles per press)
- **Tile-Based**: Player snaps to tile centers
- **Collision Detection**: Prevents movement into water tiles

### ⚔️ Attack System
- **X + Arrow Keys**: Attack in direction
- **Visual Feedback**: Thin directional rectangles
- **Timed Display**: Attacks visible for 30 frames (0.5 seconds)
- **4-Directional**: UP, DOWN, LEFT, RIGHT attacks

### 🗺️ Map System
- **Tile-Based Rendering**: 32x32 pixel tiles
- **Terrain Types**: Grass, Water, Mountains, Forest
- **Camera Culling**: Only draws visible map portions
- **Procedural Generation**: Seeded and random map creation
- **File I/O**: Save/load maps from text files
- **Boundary Handling**: Black squares beyond map edges

### 📷 Camera System
- **Player-Centered**: Camera follows player automatically
- **Smooth Scrolling**: Real-time camera updates
- **Viewport Culling**: Performance optimization
- **Coordinate Translation**: World-to-screen coordinate mapping

### 👥 Entity System
- **Multiple Types**: Players, Enemies, Items, NPCs
- **Mass Population**: Supports thousands of entities
- **Performance Optimized**: Only renders visible entities
- **Tile-Centered**: All entities align to tile grid
- **Type-Based Rendering**: Different colors per entity type

## Technical Details

### Performance Optimizations
- **Viewport Culling**: Only renders visible tiles and entities
- **Camera-Based Rendering**: Efficient coordinate transformations
- **Entity Culling**: Entities outside camera view aren't drawn
- **Tile-Based Calculations**: Grid-aligned positioning for consistency

### Coordinate Systems
- **World Coordinates**: Absolute positions in game world
- **Screen Coordinates**: Relative to camera viewport
- **Tile Coordinates**: Grid-based tile positions
- **Centered Positioning**: Entities centered within tiles

### Map Format
Maps are stored as space-separated integers in text files:
- `0` = Grass (green)
- `1` = Water (blue) - blocks movement
- `2` = Mountain (gray)
- `3` = Forest (dark green)

## Controls

| Input | Action |
|-------|--------|
| Arrow Keys | Move (1 tile) |
| Z + Arrow Keys | Fast move (2 tiles) |
| X + Arrow Keys | Attack in direction |
| R | Reset player to starting position |
| Escape | Exit game |

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install pygame
   ```

2. **Run the Game**:
   ```bash
   python main.py
   ```

3. **Generate New Map** (optional):
   ```python
   # Uncomment these lines in main.py:
   game_engine.map_engine.generate_random_map(width=3000, height=2000)
   game_engine.map_engine.save_map("random_map.txt")
   ```

## Configuration

Edit `statics.py` to customize:
- Tile size and map dimensions
- Player speed and size
- Attack range and duration
- Colors and visual settings
- Performance settings (FPS)

## Architecture Notes

- **Modular Design**: Separated concerns across multiple files
- **Entity-Component Pattern**: Flexible entity system
- **Observer Pattern**: Camera follows player automatically
- **Strategy Pattern**: Different entity types with type-specific rendering
- **Performance-First**: Optimized rendering pipeline
- **Extensible**: Easy to add new entity types and behaviors

## Future Enhancements

- Sound system integration
- Animation system
- Multiplayer support
- Advanced AI for NPCs/enemies
- Quest and inventory systems
- Level progression
- Save/load game states
