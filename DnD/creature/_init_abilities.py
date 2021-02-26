# inherited by CreatureInitialise

from ._base import CreatureBase
from ..dice.ability import Ability
import warnings
import math
from typing import *

class CreatueInitAble(CreatureBase):

    def _score2bonus(self, score: int):
        return int(( int(score) - 10 ) / 2)

    def _initialise_abilities(self):
        """
        Rewritten so that cleaning module does the cleaning.
        Formerly it would complain if bonus and score both present.
        Currently set so score takes precedence.

        :return: None.
        """
        self.able = 1  # has abilities. if nothing at all is provided it goes to zero. This is for rocks...
        # ---------- set blanks --------------------
        blank_abilities = {ab: None for ab in self.ability_names}
        if 'ability_bonuses' not in self.settings:
            self.settings['ability_bonuses'] = blank_abilities
        else:
            self.settings['ability_bonuses'] = {**blank_abilities, **self.settings['ability_bonuses']}
        if 'abilities' not in self.settings:
            self.settings['abilities'] = blank_abilities
        else:
            self.settings['abilities'] = {**blank_abilities, **self.settings['abilities']}
        # ---------- alter --------------------
        for ab in self.ability_names:
            score = int(self.settings['abilities'][ab])
            bonus = int(self.settings['ability_bonuses'][ab])
            self.set_ability_die(ability_name=ab, score=score, bonus=bonus)

    def set_ability_die(self, ability_name:str, score:Optional[int]=None, bonus:Optional[int]=None):
        ability_die = self[ability_name]
        assert ability_name in self.ability_names, f'{ability_name} is not in {self.ability_names}'
        if score is not None and bonus is not None:
            if self._score2bonus(score) != bonus:
                warnings.warn(f'Mismatch with ability {ability_name}: bonus={bonus}, score={score}')
            ability_die.score = score
            ability_die.bonus = bonus
        elif score is not None:
            ability_die.score = score
        elif bonus is not None:
            ability_die.bonus = bonus
        else:
            pass


    def change_attribute(self, **abilities):
        """
        Setting an ability attribute directly does not result in a recalculation.
        For example:

        >>> slashr = Creature('troll')
        >>> slashr.abilities['cha'] = 16

        This will not change the stats dependent on that ability.
        This method attempts to change the dependent abilities.
        A late addition, so the code does not make use of it.
        :param attributes: key value pair
        :return: None
        """
        raise DeprecationWarning # TODO REMOVE ENTIRELY
        for attr in abilities:
            attr = attr[0:3].lower()  # just in case
            if attr in self.abilities:
                old_attr = self.abilities[attr]
                self.abilities[attr] = int(abilities[attr])
                delta = int(self.abilities[attr] / 2 - 5) - int(old_attr / 2 - 5)
                old_bonus = self.ability_bonuses[attr]
                self.ability_bonuses[attr] += delta  # it might differ for some reason...
                # con does not change
                if attr == "str":
                    pass
                elif attr == "dex":
                    pass
                elif attr == "con":
                    pass
                elif attr == "int":
                    pass
                elif attr == "wis":
                    pass
                elif attr == "cha":
                    pass
            else:
                raise ValueError('Unrecognised ability')