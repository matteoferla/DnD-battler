from ._base import CreatureBase
from typing import *
import json
from ..dice import AttackRoll

class CreatureLevel(CreatureBase):
    def set_level(self, level: int, hp:Optional[int]=None, **other):
        """
        Alter the level of the creature.
        :param level: opt. int, the level. if absent it will set it to the stored level.
        :return: nothing. changes self.
        """
        level = int(level)
        old_level = self.level
        if hp is not None:
            self.hp = int(hp)
        elif old_level == 0:  # zero???
                self.recalculate_hp()
        else:
            for x in range(level - old_level):
                self.hp += self.hit_die.roll() + self.con.bonus
        self.level = level
        self.starting_hp = self.hp
        self.proficiency.level = level

    def recalculate_hp(self, max_level_one=True):
        self.hp = 0
        if max_level_one:
            self.hit_die.crit = 1  # Not-RAW: first level is always max for PCs, but not monsters.
        for x in range(self.level):
            self.hp += self.hit_die.roll()

    def set_ac(self,
               ac:Optional[int]=None,
               armor_bonus: Optional[int]=None,
               armour_name: Optional[str]=None,
               armor_ability_name:Optional[str]=None, **kwargs):
        if armour_name:
            self.armor.name = armour_name
        if armor_ability_name:
            # so for monk armor_ability_name='dex+str'
            self.armor.ability_dice = [self[ability_name] for ability_name in armor_ability_name.split('+')]
        if ac:
            self.armor.ac = int(ac)
        elif armor_bonus:
            self.armor.bonus = int(armor_bonus)
        else:
            pass

    def parse_attacks(self, attacks: Optional=None, attack_parameters:Optional=None, **others):
        """
        Two options.
        Old way via ``attack_parameters`` or
        via ``attacks``, a dictionary of name, damage_dice, attack_modifier, ability_die
        Alternatively one could fill Creature.attacks manually with a list of AttackRolls.


        :param attacks:
        :param attack_parameters:
        :return:
        """
        if attacks:
            return [AttackRoll.parse_attack(**{'ability_die': self.str, **attack}) for attack in attack_parameters]
        elif attack_parameters:
            if isinstance(attack_parameters, str):
                attack_parameters = json.loads(attack_parameters)
            return [AttackRoll.parse_list_attack(attack, self.str) for attack in attack_parameters]
        else:
            return []