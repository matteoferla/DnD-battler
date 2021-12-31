"""
These "weapons" are attacks, not weapons per se.
They are bound to a creature.

The idea is that beyond the standard weapons more exotic ones can be added.
Finess is a quality that springs to mind.

TODO the standard weapons will be loaded from a JSON or a CSV file.
 for now, they are hardcoded here temporarily.

"""
from .action import Action
from .melee import MeleeAttack
from ..dice import AttackRoll, Dice
from .enums import AttackType
from typing import *
__all__ = ['equip_standard_weapon', 'weapons']

# todo make into json/csv
weapons = {'club': 4,
           'greatclub': 8,
           'dagger': 4,
           'shortsword': 6,
           'longsword': 8, 'bastardsword': 10, 'greatsword': 12,
           'rapier': 8, 'scimitar': 6, 'sickle': 4,
           'handaxe': 6, 'battleaxe': 8, 'waraxe': 10, 'greataxe': 12,
           'javelin': 6, 'spear': 6, 'flail': 8, 'glaive': 10, 'halberd': 10, 'lance': 12, 'pike': 10,
           'trident': 6,
           'war pick': 8,
           'lighthammer': 4, 'mace': 6, 'warhammer': 8,
           'quaterstaff': 6, 'morningstar': 8, 'punch': 1,
           'whip': 4}

# todo make into a class method once all set up
def equip_standard_weapon(creature,
                          weapon_name: str,
                          modifier:int=0) -> Action:
    """
    This creates the attack but does not add it to creature.actions
    """
    # ## determine if weapon is known
    if weapon_name not in weapon_name:
        raise ValueError(f'{weapon_name} does not appear in the list of weapons known. {list(weapons.keys())}')
    # ## get info
    # todo change:
    weapon_data = weapons[weapon_name]  # int now, Dict later!
    ability_name = 'str'
    damage = weapon_data
    print(damage)
    damage_dice = Dice(damage, 0)
    attack_roll = AttackRoll(name=weapon_name,
                             ability_die=creature[ability_name],
                             damage_dice=damage_dice,
                             modifier=modifier
                             )
    # ## determine weapon type
    # todo for now, everything is a melee weapon.
    attack_type = AttackType.melee
    if attack_type == AttackType.melee:
        SpecificAttack = MeleeAttack
    else:
        raise NotImplementedError('Ranged etc. attacks are made yet.')
    return SpecificAttack(creature=creature,
                          name=weapon_name,
                          attack_roll=attack_roll
                            )

