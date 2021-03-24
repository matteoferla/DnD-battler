from ._base import CreatureBase
from ..actions import Action, MeleeAttack, Multiattack
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
        return None

#TODO Make self.actions
# TODO parse_attacks(attack_parameters=) NO

    def parse_attack(self, attack) -> Action:
        if attack is None:  # nothing to be done.
            return None
        elif isinstance(attack, Action):
            return attack  # already an action.
        elif isinstance(attack, dict):
            roll = AttackRoll.parse_attack(**{'ability_die': self.str, **attack})
            return MeleeAttack(creature=self, name=name, attack_roll=roll)
        elif isinstance(attack, list):
            roll = AttackRoll.parse_list_attack(attack, self.str)
            return MeleeAttack(creature=self, name=name, attack_roll=roll)
        else:
            raise TypeError(f'attack is of type {type(attack)}')

    def parse_attacks(self,
                      attacks: Optional[List[dict, Action, AttackRoll]]=None, **others) -> Action:
        """
        A multiattack is a curious case where a creature can do multiple attacks as a single action.
        Although technically it could do a single action –these are not added.
        The values of ``attacks`` if more than one
        are interpreted as a multiattack if multiple, regular if one.

        One could fill Creature.actions manually with the Action directly.
        Or use this.
        Due to legacy reasons it is heavily overloaded.
        attacks is a list of "attacks" or a single "attack".
        This being an action, attackroll, dict or list
        """
        # -----------it is not a list ----------------------------------------
        if attacks is None:
            return None  # What?
        elif len(attacks) == 0:
            return None # ...
        elif isinstance(attacks, str):
            # go round again after de-json-ing.
            return self.parse_attacks(json.loads(attacks))
        elif isinstance(attacks, (dict, AttackRoll, Action)):
            # single attack. (list form solved below)
            return self.parse_attack(attacks)
        elif not isinstance(attacks, (list, tuple)):
            raise TypeError(f'Attacks is not list or tuple, but {type(attacks)}')
        # -----------it is a list ----------------------------------------
        elif isinstance(attacks[0], str):
            # attacks[0] is a name. single attack in list form.
            return self.parse_attack(attacks)
        elif not isinstance(attacks[0], Action):
            # attacks need converting first
            attacks = [self.parse_attack(attack) for attack in attacks]
            return self.parse_attacks(attacks)
        elif len(attacks) > 1:
            # attacks is a list of actions
            multi = Multiattack(creature=self, name='multiattack', actions=attacks)
            return multi
        else:
            # single attack
            return attacks[0]