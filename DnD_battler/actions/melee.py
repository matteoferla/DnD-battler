from ..dice import AttackRoll
from typing import *
from .enums import AttackType, TargetChoice
from .action import Action
from .enums import AttackType
from typing import *


class MeleeAttack(Action):

    def __init__(self,
                 creature,
                 name : str,
                 attack_roll: AttackRoll,
                 **kwargs):
        super().__init__(creature=creature, name=name, typology=AttackType.melee,  **kwargs)
        self.attack_roll = attack_roll

    def __str__(self):
        return f'{self.type} "{self.name}" of {self.creature.name} dealing {self.attack_roll.damage_dice} damage'

    def find_targets(self):
        try:
            return self.creature.arena.find(self.arena.target, self)[0]
        except IndexError:
            raise Victory()

    def do(self):
        opponent = self.find_target()
        advantage = self.creature.check_advantage(opponent)
        self.log.debug(f"{self.name} attacks {opponent.name} with {self.name}")
        # This was the hit method. put here for now.
        damage = self.attack_roll.attack(opponent.armor.ac, advantage=advantage)
        if damage > 0:
            opponent.take_damage(damage)
            self.on_damage(opponent, damage)
            self.creature.tally['damage'] += damage
            self.creature.tally['hits'] += 1
        else:
            self.creaturer.tally['misses'] += 1

    def on_damage(self, opponent, amount: int):
        """
        Method to be overridden. called on damage.
        eg. triggering a save roll.

        :param opponent: to whom the damage was delt
        :type opponent: Creature
        :param amount:
        :return:
        """
        pass

    def absolute_score(self):
        return self.attack_roll.damage_dice.mean()