"""
These "weapons" are attacks, not weapons per se.
They are bound to a creature.

"""
from .melee import MeleeAttack

def equip_club(creature, ability_name: str = 'str'):
    return MeleeAttack(creature=creature,
                       name='club',
                       attack_roll=AttackRoll(name='club',
                                              ability_die=creature[ability_name],
                                              damage_dice=Dice(4, 0),
                                              modifier=0)
                       )
