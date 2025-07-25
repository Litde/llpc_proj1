from game_engine import GameEngine, AttackPattern, Weapon
from interfaces import WeaponType
import statics

def main(game_engine: GameEngine):

    attack_pattern_pike = AttackPattern(
        pattern_type="Pike",
        pattern_data=[
            (0,0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)
        ]
    )

    attack_pattern_sword = AttackPattern(
        pattern_type="Sword",
        pattern_data=[
            (0,0), (0, 1), (0, 2), (-1, 1), (1, 1)
        ]
    )

    attack_pattern_hammer = AttackPattern(
        pattern_type="Hammer",
        pattern_data=[
            (0,0), (0, 1), (0, 2), (0, 3), (-1, 1), (-1, 2), (-1, 3), (1, 1), (1, 2), (1, 3)
        ]
    )

    sword = Weapon(
        name="Sword",
        weapon_type=WeaponType.SWORD,
        damage=10,
        attack_pattern=attack_pattern_sword,
        attack_duration=statics.ATTACK_DURATION_FRAMES,
        attack_cooldown=5,
    )

    hammer = Weapon(
        name="Hammer",
        weapon_type=WeaponType.HAMMER,
        damage=45,
        attack_pattern=attack_pattern_hammer,
        attack_duration=statics.ATTACK_DURATION_FRAMES,
        attack_cooldown=45,
    )

    pike = Weapon(
        name="Pike",
        weapon_type=WeaponType.PIKE,
        damage=15,
        attack_pattern=attack_pattern_pike,
        attack_duration=statics.ATTACK_DURATION_FRAMES,
        attack_cooldown=45,
    )

    game_engine.weapons_list[WeaponType.SWORD] = sword
    game_engine.weapons_list[WeaponType.HAMMER] = hammer
    game_engine.weapons_list[WeaponType.PIKE] = pike

