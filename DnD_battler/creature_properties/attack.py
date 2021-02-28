from ..dice import AttackRoll
from typing import *

class Action:
    def __init__(self, caster, name :str, **kwargs):
        self.caster = caster
        self.name = name

    def

class Attack:

    def __init__(self, caster, attack_rolls: List[AttackRoll]):
        self.caster = caster
        self.attack_rolls = attack_rolls

    def attack(self, opponent):
        for attack_roll in self.attack_rolls:
            try:
                opponent = self.arena.find(self.arena.target, self)[0]
            except IndexError:
                raise Victory()
            self.log.debug(f"{self.name} attacks {opponent.name} with {self.attacks[i].name}")
            # This was the hit method. put here for now.
            damage = self.attack_roll.attack(opponent.armor.ac, advantage=self.check_advantage(opponent))
            if damage > 0:
                opponent.take_damage(damage)
                self.on_damage()
                caster.tally['damage'] += damage
                caster.tally['hits'] += 1
            else:
                caster.tally['misses'] += 1

    def on_damage(self, attacker, opponent, amount: int):
        """
        Method to be overridden. called on damage.

        :param attacker: who delt the damage
        :type attacker: Creature
        :param opponent: to whom the damage was delt
        :type opponent: Creature
        :param amount:
        :return:
        """
        pass