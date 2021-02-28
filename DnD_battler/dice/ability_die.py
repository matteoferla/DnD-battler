from .dice import Dice
from ..creature_properties.proficiency import Proficiency
from typing import *
# from ..creature_properties.size import Size # Size no longer plays a role in AC or abilities.


class AbilityDie(Dice):
    def __init__(self, bonus: int = 0, proficiency: Proficiency=None):
        """
        A dice that has additional a ``score`` and a ``temp_modifier``
        temp_modifier is for poisons etc. not for skills modifiers or proficiency bonus

        :param bonus:
        :param proficieny:
        """
        super().__init__(num_faces=20,
                         bonus=bonus)
        self.temp_modifier = 0
        self.score = 10 + self.bonus * 2  # ability score
        if proficiency is None:
            proficiency = Proficiency(0, 0)
        self.proficiency = proficiency
        self.crit = 0
        self.advantage = 0

    @classmethod
    def from_score(cls, score: int = 10):
        """
        Creates a new die. Problematic as it will not change the skills/attack rolls linked to it.

        :param score:
        :return:
        """
        self = cls(bonus=int(score - 10 / 2))
        self.score = score
        return self

    def _single_roll(self, avg=None):
        return super().base_roll(avg)

    def base_roll(self, advantage:Optional[int]=None, avg=None, success_on_crit=True):
        """
        returns the roll without the bonuses.
        RAW in 5e, a crit on an ability roll is not a given success,

        :param avg:
        :param success_on_crit:
        :return:
        """
        self.crit = 0
        # ----- get roll --------------------------
        if advantage is None:
            advantage = self.advantage
        if advantage == 0:
            roll = self._single_roll(avg)  # this has not got the bonus included.
        elif advantage <= -1:  # AKA disadvatage
            roll = sorted([self._single_roll(avg) for i in range(abs(advantage)+1)])[0]
        elif advantage >= 1:
            roll = sorted([self._single_roll(avg) for i in range(abs(advantage)+1)], reverse=True)[0]
        # ---- resolve crit -----------------------
        if not success_on_crit:
            pass
        elif roll == 20:
            self.log.debug(f'Crit!')
            roll = float('inf')
            self.crit = 1
        elif roll == 1:
            self.log.debug(f'Fumble!')
            roll = float('-inf')
            self.crit = -1
        else:
            pass # not a crit.
        # ------- return --------------------------
        return roll

    def roll(self, advantage:Optional[int]=None, avg=None, success_on_crit=True):
        return self.base_roll(advantage, avg, success_on_crit) + self.proficiency.bonus + self.temp_modifier

    @staticmethod
    def score2bonus(score: int):
        return int((int(score) - 10) / 2)

    @staticmethod
    def bonus2score(bonus: int):
        return int(bonus) * 2 + 10
