# Game Engine Project

A comprehensive tile-based 2D game engine built with Python and Pygame, featuring camera-based rendering, entity management, combat systems, and inventory management.

## Project Structure

```
llpc_proj1/
├── README.md                # Project documentation
├── main.py                  # Main game loop and input handling
├── game_engine.py          # Core game engine classes
├── interfaces.py           # Entity system, UI classes, and enums
├── statics.py             # Game constants and configuration
├── maps/                  # Map data files
│   └── test_map.txt       # Game map file
└── __pycache__/          # Python bytecode cache
```

## File Descriptions

### `main.py`
- **Purpose**: Entry point and main game loop
- **Features**:
  - Game initialization and window management (1920x1080)
  - Advanced input handling with key combinations
  - Entity population (1000 items + 1000 enemies)
  - Real-time attack and movement processing

### `game_engine.py`
Core game engine containing multiple specialized classes:

#### `GameEngine`
- Main orchestrator and initialization manager
- Coordinates all subsystems (GameLogic, MapEngine, Player, Camera)
- Manages game state and initialization flow

#### `GameLogic`
- **Entity Management**: Creates, tracks, and disposes entities
- **Damage System**: Handles directional combat with one-hit-per-attack logic
- **Coin Collection**: Manages item pickup and inventory integration
- **Entity Population**: Distributes entities across map with proper tile centering
- **Performance**: Cleanup of disposed entities to prevent memory leaks

#### `MapEngine`
- **Rendering Pipeline**: Camera-based tile culling for optimal performance
- **Attack Visualization**: Directional attack indicators with proper timing
- **Map Management**: Generation, loading, saving of tile-based maps
- **UI Integration**: Inventory display and UI element rendering
- **Coordinate Systems**: World-to-screen transformations

#### `Inventory` (UI System)
- **Slot-Based Interface**: 10-slot inventory with visual indicators
- **Item Display**: Color-coded items with name indicators
- **Toggle System**: Show/hide with 'I' key
- **UI Inheritance**: Extends base UI class for consistent interface

#### `Player`
- **Movement System**: Tile-centered positioning with collision detection
- **Inventory Integration**: Built-in inventory management
- **Attack System**: Directional attacks with visual feedback
- **Collision Detection**: Center-based collision for precise interaction

#### `Camera`
- **Player Tracking**: Automatic camera following
- **Performance Optimization**: Viewport-based rendering culling
- **Coordinate Translation**: Seamless world-to-screen mapping

### `interfaces.py`
- **Entity System**: Base Entity class with center-based collision detection
- **UI Framework**: Base UI class with specialized Inventory implementation
- **Enums**: 
  - `AttackDirection` (UP, DOWN, LEFT, RIGHT, NONE)
  - `EntityType` (PLAYER, ENEMY, ITEM, NPC)
- **Entity Safety**: Disposal pattern preventing operations on destroyed entities
- **Collision System**: Center-based rectangle collision for precise interactions

### `statics.py`
Configuration constants for all game systems:
- **Map Settings**: Tile size (32px), dimensions, terrain colors
- **Player Configuration**: Size, speed, starting position, colors
- **Combat Settings**: Attack range (2 tiles), duration (30 frames), damage
- **Entity Properties**: Colors, sizes, and health values for all entity types
- **Performance**: FPS settings and optimization parameters

## Key Features

### 🎮 Advanced Movement System
- **Arrow Keys**: Standard movement (1 tile per press)
- **Z + Arrow Keys**: Fast movement (2 tiles per press)
- **Tile-Centered**: All entities snap to tile centers for consistency
- **Collision Detection**: Water tile prevention with boundary checking
- **Reset Function**: 'R' key returns player to starting position

### ⚔️ Combat System
- **Directional Attacks**: X + Arrow keys for 4-directional combat
- **Visual Feedback**: Attack area visualization with directional indicators
- **Damage System**: 10 damage per hit with health management
- **One-Hit-Per-Attack**: Entities can only be damaged once per attack cycle
- **Entity Targeting**: Attacks affect enemies and NPCs, not items
- **Attack Duration**: 30-frame attack window (0.5 seconds at 60 FPS)

### 🎒 Inventory System
- **Slot-Based UI**: 10 inventory slots with visual item representation
- **Item Collection**: Automatic pickup of coins and items on contact
- **Toggle Interface**: 'I' key to show/hide inventory
- **Item Display**: Color-coded items with name indicators
- **Count Tracking**: Real-time inventory item count display
- **UI Inheritance**: Consistent interface design pattern

### 🗺️ Advanced Map System
- **Multi-Terrain**: Grass, Water, Mountains, Forest with movement rules
- **Procedural Generation**: Seeded map generation with varied terrain distribution
- **File I/O**: Save/load maps in human-readable text format
- **Boundary Management**: Black void rendering beyond map edges
- **Performance Optimization**: Only renders visible map sections

### 📷 Camera System
- **Auto-Following**: Camera automatically centers on player
- **Smooth Rendering**: Real-time camera updates with no stuttering
- **Viewport Culling**: Only draws tiles and entities within view
- **Coordinate Translation**: Seamless world-to-screen transformations
- **Debug Mode**: Optional camera location display

### � Entity Management System
- **Multiple Types**: Players, Enemies (100 HP), Items (coins), NPCs
- **Mass Population**: Efficiently handles thousands of entities (2000+ tested)
- **Smart Disposal**: Automatic cleanup of destroyed entities prevents memory leaks
- **Center-Based Collision**: Precise collision detection using entity centers
- **Health System**: Enemies with health management and automatic disposal at 0 HP
- **Type-Based Rendering**: Distinct colors and behaviors per entity type

### 🎯 Performance Optimizations
- **Viewport Culling**: Only renders visible tiles and entities
- **Entity Culling**: Entities outside camera view aren't processed for rendering
- **Disposal Pattern**: Automatic cleanup prevents memory leaks
- **Efficient Collision**: Center-based collision detection for speed
- **Attack Optimization**: One-damage-per-attack prevents redundant calculations
- **Camera-Based Rendering**: Minimal coordinate transformations

## Technical Implementation

### Combat System Architecture
- **Damage Tracking**: Set-based tracking prevents multiple hits per attack
- **Directional Areas**: Precise attack rectangles based on player position
- **Entity Filtering**: Attacks only affect valid targets (enemies, NPCs)
- **Timer Management**: Attack duration and cooldown handling
- **Visual Synchronization**: Attack display matches damage areas exactly

### Coordinate Systems
- **World Coordinates**: Absolute positions in game world (pixels)
- **Screen Coordinates**: Camera-relative viewport positions
- **Tile Coordinates**: Grid-based tile positions (32x32 pixel tiles)
- **Centered Positioning**: All entities centered within tiles for consistency

### Inventory Architecture
- **UI Inheritance**: Inventory extends base UI class for consistency
- **Player Integration**: Direct inventory access through player object
- **Item Management**: Add, remove, clear operations with safety checks
- **Visual Representation**: Slot-based display with item color coding

### Map Data Format
Maps stored as space-separated integers in text files:
- `0` = Grass (green) - walkable
- `1` = Water (blue) - blocks movement
- `2` = Mountain (gray) - walkable
- `3` = Forest (dark green) - walkable

## Controls

| Input | Action |
|-------|--------|
| Arrow Keys | Move 1 tile |
| Z + Arrow Keys | Move 2 tiles (fast) |
| X + Arrow Keys | Attack in direction |
| I | Toggle inventory display |
| R | Reset player position |
| Escape | Exit game |

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Pygame library

### Installation

1. **Clone or Download the Project**:
   ```bash
   git clone <repository-url>
   cd llpc_proj1
   ```

2. **Install Dependencies**:
   ```bash
   pip install pygame
   ```

3. **Run the Game**:
   ```bash
   python main.py
   ```

### First Run
- The game loads `test_map.txt` by default
- 1000 coins and 1000 enemies will spawn on the map
- Use arrow keys to move and explore
- Press 'I' to view your inventory
- Use X+Arrow keys to attack enemies

### Generating New Maps (Optional)
Uncomment these lines in `main.py` to create new maps:
```python
game_engine.map_engine.generate_random_map(width=250, height=250)
game_engine.map_engine.save_map("new_map.txt")
```

## Gameplay

### Objectives
- **Exploration**: Navigate the procedurally generated world
- **Collection**: Gather coins that automatically go to your inventory
- **Combat**: Fight enemies using directional attacks
- **Survival**: Manage positioning to avoid enemy encounters

### Strategy Tips
- Use fast movement (Z+Arrow) for exploration
- Attack enemies to clear areas before collecting items
- Check your inventory regularly with 'I' key
- Use water tiles as natural barriers (enemies can't cross)
- Reset position with 'R' if you get stuck

## Configuration & Customization

### Easy Modifications (edit `statics.py`):
- **Tile Size**: Change `TILE_SIZE` for different grid scaling
- **Player Speed**: Modify `PLAYER_SPEED` for movement distance
- **Attack Range**: Adjust `PLAYER_ATTACK_RADIUS` for combat reach
- **Entity Counts**: Change spawn numbers in `main.py`
- **Colors**: Customize all entity and terrain colors
- **Window Size**: Modify window dimensions in `main.py`

### Advanced Customization:
- **New Entity Types**: Add to `EntityType` enum and implement rendering
- **New Terrain**: Add terrain types to map generation and rendering
- **Custom Maps**: Create text files with terrain data
- **UI Modifications**: Extend the UI class for new interface elements

## Architecture & Design Patterns

### Separation of Concerns
- **GameLogic**: Entity management, combat, item collection
- **MapEngine**: Rendering, camera, UI display, input processing
- **Player**: Movement, inventory, player-specific behavior
- **Interfaces**: Base classes, enums, shared functionality

### Design Patterns Used
- **Entity-Component**: Flexible entity system with type-based behavior
- **Observer**: Camera automatically follows player
- **Strategy**: Different entity types with specialized rendering
- **Disposal**: Safe entity cleanup pattern
- **Factory**: Entity creation through GameLogic

### Performance Architecture
- **Culling Systems**: Viewport-based rendering optimization
- **Memory Management**: Automatic disposal and cleanup
- **Efficient Collision**: Center-based detection
- **Minimal Redraws**: Only update changed screen areas

## Future Enhancements & Roadmap

### Short-term Improvements
- **Sound System**: Audio feedback for attacks, movement, item collection
- **Animation System**: Sprite-based animations for entities and attacks
- **Enemy AI**: Basic pathfinding and player-seeking behavior
- **Item Stacking**: Group similar items in inventory slots
- **Health Display**: Player health bar and damage indicators

### Medium-term Features
- **Multiple Levels**: Map progression and level transitions
- **Save System**: Persistent game state and progress
- **Quest System**: Objectives and goal-based gameplay
- **Item Types**: Different items with varied effects
- **Enhanced Combat**: Special attacks, combos, weapon types

### Long-term Vision
- **Multiplayer Support**: Network-based cooperative gameplay
- **Level Editor**: In-game map creation and editing tools
- **Mod Support**: Plugin system for community content
- **Advanced Graphics**: Sprite sheets, particle effects, lighting
- **Mobile Port**: Touch-based controls and mobile optimization

## Contributing

### Development Setup
1. Follow the installation instructions above
2. Create a new branch for features: `git checkout -b feature-name`
3. Test changes thoroughly with different map sizes and entity counts
4. Ensure no performance regressions with large entity populations

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add docstrings for all public methods
- Comment complex logic, especially coordinate transformations
- Maintain separation of concerns between classes

### Testing Areas
- **Performance**: Test with 5000+ entities to verify optimization
- **Memory**: Verify no memory leaks with long gameplay sessions
- **Edge Cases**: Test map boundaries, zero entities, empty inventory
- **Collision**: Verify attack and movement collision accuracy
- **UI**: Test inventory with maximum items and edge cases

## License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## Acknowledgments

- Built with **Pygame** - Python game development library
- Inspired by classic tile-based RPGs and roguelike games
- Thanks to the Python community for excellent documentation and examples

---

**Project Status**: Active Development
**Last Updated**: July 2025
**Python Version**: 3.7+
**Pygame Version**: 2.0+
