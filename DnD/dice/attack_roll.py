from .skill_roll import SkillRoll
from .ability_die import AbilityDie
from .dice import Dice
from typing import *


class AttackRoll(SkillRoll):
    def __init__(self, name, ability_die: AbilityDie, damage_dice: Dice, modifier: int = 0):
        super().__init__(ability_die=ability_die, modifier=modifier, success_on_crit=True)
        self.name = name
        self.damage_dice = damage_dice

    def attack(self, enemy_ac: int, advantage: Optional[int] = None) -> int:
        """
        returns an integer of the damage incurred. 0 is fail

        :param enemy_ac:
        :param advantage:
        :return:
        """
        attack_roll = self.roll(advantage=advantage)
        if attack_roll >= enemy_ac:
            # note this can allow crit trains, were one to alter the crit value.
            damage_roll = sum([self.damage_dice.roll() for i in range(self.ability_die.crit + 1)])
        else:
            damage_roll = 0
        return damage_roll

    @classmethod  # old input
    def parse_list_attack(cls, attack: list, ability_die):
        # old input. ['club', 2, 0, 4]
        return cls.parse_attack(name=attack[0],
                                ability_die=ability_die,
                                damage_dice=Dice(num_faces=[int(n) for n in attack[3:]], bonus=attack[2]),
                                attack_modifier=attack[1])

    @classmethod
    def parse_attack(cls,
                     name: str,
                     ability_die: AbilityDie,
                     damage_dice: Union[str, Dice],
                     attack_modifier: int):
        """
        Returns an Attack roll

        :param name: name of weapon...
        :param ability_die: generally creature.str ... but dex for finesse weapons or wis for shileyley
        :param damage_dice: a dice obj, str or int.
        :param attack_modifier: the weapon modifier. No proficiency or ability bonus or poison etc.
            these come from the ability_die.
        :return:
        """
        # damage_dice
        if isinstance(damage_dice, Dice):
            pass  # damage_dice is good
        elif isinstance(damage_dice, str):
            damage_dice = Dice.from_notation(damage_dice)
        elif isinstance(damage_dice, int):
            damage_dice = Dice(num_faces=damage_dice)
        else:
            raise KeyError(f'Bad damage dice specified. Please use either notation or actual Dice')
        # return
        return cls(name=name, ability_die=ability_die, damage_dice=damage_dice, modifier=int(attack_modifier))
