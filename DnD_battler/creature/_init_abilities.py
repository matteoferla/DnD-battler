# inherited by CreatureInitialise

from ._base import CreatureBase
from ..dice.ability_die import AbilityDie
from typing import *


class CreatueInitAble(CreatureBase):

    def set_ability_dice(self, **settings) -> None:
        """
        Rewritten so that cleaning module does the cleaning.
        Formerly it would complain if bonus and score both present.
        Currently set so score takes precedence.

        :return: None.
        """
        self.able = 1  # has abilities. if nothing at all is provided it goes to zero. This is for rocks...
        settings = self._sanitise_settings_for_abilities(settings)
        for ab in self.ability_names:
            score = settings['abilities'][ab]
            bonus = settings['ability_bonuses'][ab]
            self.set_ability_die(ability_name=ab, score=score, bonus=bonus)

    def set_ability_die(self, ability_name: str, score: Optional[int] = None, bonus: Optional[int] = None):
        ability_die = self[ability_name]
        # print(ability_name, ability_die.score, score, ability_die.bonus, bonus)
        assert isinstance(ability_die, AbilityDie), f'The die for {ability_name} is not a die, but {type(ability_die)}'
        assert ability_name in self.ability_names, f'{ability_name} is not in {self.ability_names}'
        if score is not None and bonus is not None:
            if AbilityDie.score2bonus(score) != bonus:
                self.log.warning(f'Mismatch with ability {ability_name}: bonus={bonus}, score={score}')
            ability_die.score = score
            ability_die.bonus = bonus
        elif score is not None:
            ability_die.score = score
            ability_die.bonus = AbilityDie.score2bonus(score)
        elif bonus is not None:
            ability_die.bonus = bonus
            ability_die.score = AbilityDie.bonus2score(bonus)
        else:
            # no change required.
            pass

    def _sanitise_settings_for_abilities(self, settings) -> dict:
        settings = {k.lower(): v for k, v in settings.items()}
        # ---------- set blanks ----------------------------------------------------------------------------------------
        blank_abilities = {ab: None for ab in self.ability_names}
        # ability_bonuses
        if 'ability_bonuses' not in settings:
            ability_bonuses = blank_abilities.copy()
        else:
            ability_bonuses = {**blank_abilities.copy(), **settings['ability_bonuses']}
        # abilities
        if 'abilities' not in settings:
            abilities = blank_abilities
        else:
            abilities = {**blank_abilities.copy(), **settings['abilities']}
        # ---------- capture odd entries -------------------------------------------------------------------------------
        full_names = {'strength': 'str',
                      'dexterity': 'dex',
                      'constitution': 'con',
                      'wisdom': 'wis',
                      'intelligence': 'int',
                      'charisma': 'cha'}
        for full_name, short_name in full_names.items():
            if full_name in settings:
                abilities[short_name] = settings[full_name]
            if f'{full_name}_bonus' in settings:
                ability_bonuses[short_name] = settings[f'{full_name}_bonus']
        # ------- capture isolated entries -----------------------------------------------------------------------------
        for ability_name in self.ability_names:
            if ability_name in settings:
                abilities[ability_name] = settings[ability_name]
            if f'ab_{ability_name}' in settings:
                ability_bonuses[ability_name] = settings[f'ab_{ability_name}']
        # ------- correct for dice -------------------------------------------------------------------------------------
        for ability_name, score in abilities.items():
            if isinstance(score, int) or score is None:
                pass # perfect
            elif isinstance(score, AbilityDie):
                abilities[ability_name] = score.score
            else:
                abilities[ability_name] = int(score)
        for ability_name, bonus in ability_bonuses.items():
            if isinstance(bonus, int) or bonus is None:
                pass  # perfect
            else:
                ability_bonuses[ability_name] = int(bonus)
        # ------- done -------------------------------------------------------------------------------------------------
        return dict(abilities=abilities,
                    ability_bonuses=ability_bonuses)

    #
    # def change_attribute(self, **abilities):
    #     """
    #     Setting an ability attribute directly does not result in a recalculation.
    #     For example:
    #
    #     >>> slashr = Creature('troll')
    #     >>> slashr.abilities['cha'] = 16
    #
    #     This will not change the stats dependent on that ability.
    #     This method attempts to change the dependent abilities.
    #     A late addition, so the code does not make use of it.
    #     :param attributes: key value pair
    #     :return: None
    #     """
    #     raise DeprecationWarning # TODO REMOVE ENTIRELY
    #     for attr in abilities:
    #         attr = attr[0:3].lower()  # just in case
    #         if attr in self.abilities:
    #             old_attr = self.abilities[attr]
    #             self.abilities[attr] = int(abilities[attr])
    #             delta = int(self.abilities[attr] / 2 - 5) - int(old_attr / 2 - 5)
    #             old_bonus = self.ability_bonuses[attr]
    #             self.ability_bonuses[attr] += delta  # it might differ for some reason...
    #             # con does not change
    #             if attr == "str":
    #                 pass
    #             elif attr == "dex":
    #                 pass
    #             elif attr == "con":
    #                 pass
    #             elif attr == "int":
    #                 pass
    #             elif attr == "wis":
    #                 pass
    #             elif attr == "cha":
    #                 pass
    #         else:
    #             raise ValueError('Unrecognised ability')
