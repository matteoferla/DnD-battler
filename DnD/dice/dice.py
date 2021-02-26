from __future__ import annotations
from typing import *
import math, random, re


class Dice:

    def __init__(self,
                 num_faces: Union[int, List[int]] = 20,
                 bonus: int = 0,
                 avg: bool = False,
                 twinned: Optional[Dice] = None,
                 role: str = "ability"):
        """
        Class to handle dice and dice rolls
        (The plural is intentional.

        :param bonus: int, the bonus added to the attack roll
        :param num_faces: list of int, the dice size.
        :param avg: boolean flag marking whether the dice always rolls average,
            like NPCs and PCs on Mechano do for attack rolls. For a one off use int(dice.mean())
        :param twinned: a dice. ja. ehrm. this is the other dice.
            attack --> damage
            The crits are passed to it. It should be a weak ref or the crits passed more pythonically.
        :param role: string, but actually on a restricted vocabulary:
            ability, damage, hd or healing. Extras can be added, but they won't trigger some things
        :return: a rollable dice!

        The parameters are set to attributes. Other attributes are:

        * critable: determined from `role` attribute
        * cirt: 0 or 1 ... or more if you want to go 3.5 and crit train.
        * advantage: trinary int. -1 is disadvantage, 0 normal, 1 is advantage.

        """
        self.twinned = self._parse_twinned(twinned)
        ##Can it crit?
        self.role = role
        if self.role == "damage" or self.role == "healing" or self.role == "hd":
            self.critable = 0
        else:
            self.critable = 1
        # stats
        self.bonus = int(bonus)
        self.num_faces = self._parse_num_faces(num_faces)
        # ------------- current state -------------------
        self.advantage = 0
        self.crit = 0  # multiplier+1. Actually you can't get a crit train anymore.
        self.avg = avg

    def _parse_twinned(self, twinned: Optional[Dice] = None) -> Union[None, Dice]:
        # simply check the value is sane.
        if twinned is None:
            return None
        elif isinstance(twinned, self.__class__):
            return twinned
        else:
            raise TypeError(f'Twinned: {type(twinned)}')

    def _parse_num_faces(self, num_faces: Union[int, List[int]]) -> List[int]:
        if isinstance(num_faces, list):
            return [int(i) for i in num_faces]
        elif isinstance(num_faces, int):
            return [num_faces]
        else:
            raise TypeError(f'num_faces is {type(num_faces)}')

    # --------- Alt entry ------------------------------------------------------------------

    def multiroll(self, verbose=0):
        """
        A roll that is not a d20. It adds the bonus and rolls (x2 if a crit).

        :param verbose:
        :return:
        """
        if self.avg:  # NPC rolls
            result = int(sum(num_faces / 2 + 0.5 for num_faces in self.num_faces))
        else:
            result = sum(random.randint(1, num_faces) for num_faces in self.num_faces)
        if self.crit:
            result *= 2
        return result + self.bonus

    def icosaroll(self, verbose=0):
        """
        A roll that is a d20. It rolls advantage and disadvatage and calls `_critcheck`.

        :param verbose:
        :return:
        """
        self.crit = 0
        if self.advantage == 0:
            return self._crit_check(random.randint(1, 20), verbose) + self.bonus
        elif self.advantage == -1:  # AKA disadvatage
            return self._crit_check(sorted([random.randint(1, 20), random.randint(1, 20)])[0], verbose) + self.bonus
        elif self.advantage == 1:
            return self._crit_check(sorted([random.randint(1, 20), random.randint(1, 20)])[1], verbose) + self.bonus

    def _crit_check(self, result, verbose=0):
        """
        Checks if the dice is a crit.

        :param result: dice roll result.
        :param verbose: a debug paramater that I really ought to write out of the code.
        :return: alters the dice roll to -999 if a crit fail or 999 and adds a crit marker to the twinned dice (_i.e._ the attack dice)
        """
        if not self.critable:
            print("DEBUG: A crit check was called on an uncritable roll ", self.role)
            return result
        elif result == 1:
            if verbose:
                verbose.append("Fumble!")
            return -999  # automatic fail
        elif result == 20:
            if verbose:
                verbose.append("Crit!")
            if self.twinned: self.twinned.crit = 1
            return 999  # automatic hit.
        else:
            return result

    def roll(self, verbose=0):
        # THIS ASSUMES NO WEAPON DOES d20 DAMAGE!!
        # Dragonstar and Siege engines don't obey this.
        """
        The roll method, which calls either icosaroll or multiroll.

        :param verbose: debug
        :return: the value rolled (and alters the dice too if need be)
        """
        if not self.num_faces:
            raise Exception('A non-existant dice has been attempted to be rolled')
        # elif self.num_faces[0] == 20:
        elif self.critable:
            # the problem is crits and adv and only d20 can.
            # Nothing deals d20 damage, but someone might try.
            return self.icosaroll(verbose)
        else:
            return self.multiroll(verbose)

    # --------- Alt entry ------------------------------------------------------------------

    @classmethod
    def from_notation(cls, notation: str, **kargs) -> Dice:
        """
        2d6+2 to Dice

        :param notation: 2d6+2
        :return:
        """
        num_faces = []
        bonus = 0
        for term in notation.split('+'):
            term = term.strip()
            if 'd' in term:
                num, faces = re.match(r'(\d*)d(\d+)', notation).groups()
                if num == '':
                    num = 1
                for i in range(int(num)):
                    num_faces.append(int(faces))
            elif term.isdecimal():
                bonus = int(term)
            elif term == '':
                pass
            else:
                raise ValueError(f'Notation {notation}. issue with {term}')
        return cls(num_faces=num_faces,
                   bonus=bonus,
                   **kargs)

    # ----------------- utils ---------------------------------------------------

    def __str__(self):
        """
        This is rather inelegant piece of code and is not overly flexible.
        If the dice fail to show, they will still work.

        :return: string in dice notation.
        """
        s = ''
        if len(self.num_faces) == 1:
            s += 'd' + str(self.num_faces[0]) + '+'
        elif len(self.num_faces) == 2 and self.num_faces[0] == self.num_faces[1]:
            s += '2d' + str(self.num_faces[0]) + '+'
        elif len(self.num_faces) == 2 and self.num_faces[0] != self.num_faces[1]:
            s += 'd' + str(self.num_faces[0]) + '+d' + 'd' + str(self.num_faces[1]) + '+'
        elif len(self.num_faces) == 3 and self.num_faces[0] == self.num_faces[1] == self.num_faces[1]:
            s += '3d' + str(self.num_faces[0]) + '+'
        elif len(self.num_faces) == 3 and self.num_faces[0] != self.num_faces[1]:
            s += 'd' + str(self.num_faces[0]) + '+d' + str(self.num_faces[1]) + '+d' + str(self.num_faces[1]) + '+'
        else:
            for x in range(len(self.num_faces)):
                s += 'd' + str(self.num_faces[x]) + '+'
        s += str(self.bonus)
        return s

    def __len__(self):
        return len(self.num_faces)

    def mean(self):
        """
        The average roll on a dice is 3.5 because the lowest is 1, not zero.
        Hence the len addition.
        Unlike avg, it is not rounded down.
        """
        return (sum(self.num_faces) + len(self)) / 2 + self.bonus