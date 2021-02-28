from .ability_die import AbilityDie
from typing import *
from ..log import log

class SkillRoll:

    log = log

    def __init__(self, ability_die: AbilityDie, modifier: int = 0, success_on_crit=True):
        """
        Meant for an ability check or a saving throw.
        This allows to add an extra modifier to the ability_die (in addition to ability bonus and proficiency)
        RAW in 5e: a crit on an ability roll is not a given success.

        :param ability_die:
        :param modifier:
        :param success_on_crit:
        """
        self.ability_die = ability_die
        self.success_on_crit = success_on_crit
        self.modifier = modifier

    def base_roll(self, advantage:Optional[int]=None) -> int:
        return self.ability_die.base_roll(advantage=advantage, success_on_crit=self.success_on_crit)

    def roll(self, advantage:Optional[int]=None) -> int:
        return self.base_roll(advantage=advantage) + self.bonuses

    @property
    def bonuses(self):
        return self.ability_die.bonus + self.ability_die.proficiency.bonus + self.modifier

    def __str__(self):
        return f'{self.ability_die}+{self.ability_die.proficiency.bonus}+{self.modifier}'


#
#         self.ability_die = ability_die
#         # super().__init__(num_faces=20,
#         #                  bonus=bonus,
#         #                  role='ability')
#         self.temp_modifier = 0
#         self.score = 10 + self.bonus * 2  # ability score
#         self.twinned = self._parse_twinned(twinned)
#         ##Can it crit?
#         self.role = role
#         if self.role == "damage" or self.role == "healing" or self.role == "hd":
#             self.critable = 0
#         else:
#             self.critable = 1
#         # stats
#         self.bonus = int(bonus)
#         self.num_faces = self._parse_num_faces(num_faces)
#         # ------------- current state -------------------
#         self.advantage = 0
#         self.crit = 0  # multiplier+1. Actually you can't get a crit train anymore.
#         self.avg = avg
#

#
#
#
#
#
# class Skill:
#
#     def __init__(self, ability_die: Ability, modifier: int = 0, success_on_crit=True):
#         """
#         Meant for an ability check, a saving throw, or an attack roll
#         RAW in 5e, a crit on an ability roll is not a given success,
#
#         :param ability_die:
#         :param modifier:
#         :param success_on_crit:
#         """
#         self.ability_die = ability_die
#         self.success_on_crit = success_on_crit
#         self.modifier = modifier
#         # ------------- current state -------------------
#         self.advantage = 0
#         self.crit = 0  # multiplier+1. Actually you can't get a crit train anymore.
#
#         ##Can it crit?
#         self.role = role
#         if self.role == "damage" or self.role == "healing" or self.role == "hd":
#             self.critable = 0
#         else:
#             self.critable = 1
#
#     def roll(self):
#         pass
#
#


