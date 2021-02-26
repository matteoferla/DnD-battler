from .dice import Dice
from typing import *


class Ability(Dice):
    def __init__(self, bonus: int = 0):
        """
        A dice that has additional a ``score`` and a ``temp_modifier``

        :param bonus:
        """
        super().__init__(num_faces=20,
                         bonus=bonus,
                         role='ability')
        self.temp_modifier = 0
        self.score = 10 + self.bonus * 2  # ability score

    @classmethod
    def from_score(cls, score: int = 10):
        self = cls(bonus=int(score - 10 / 2))
        self.score = score
        return self

    def roll(self):
        return super().roll() + self.temp_modifier
