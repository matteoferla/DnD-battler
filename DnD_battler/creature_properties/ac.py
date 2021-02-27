from ..dice import AbilityDie
from typing import *


class AC:
    def __init__(self, ability_dice: List[AbilityDie], bonus: int = 0, name: str = 'unnamed'):
        self.ability_dice = ability_dice
        self.name = name
        self.bonus = bonus

    @property
    def ability_bonus(self):
        return sum([d.bonus + d.temp_modifier for d in self.ability_dice])

    def get_ac(self):
        return self.ability_bonus + self.bonus  # proficiency is not added to AC.

    def set_ac(self, value):
        self.bonus = value - self.ability_bonus

    ac = property(get_ac, set_ac)
