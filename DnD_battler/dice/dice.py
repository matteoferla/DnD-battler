from __future__ import annotations
from typing import *
import random, re
from collections import Counter
from ..log import log

class Dice:

    log = log

    def __init__(self,
                 num_faces: Union[int, List[int]] = 20,
                 bonus: int = 0,
                 avg: bool = False):
        """
        Generic set of dice rolls.
        The plural is intentional: if the roll is 2d8+1, two dice are rolled.
        These do not crit. For crittable dice see ability

        :param num_faces: list or single integer of number of faces
        :param bonus: int, the bonus added to the attack roll
        :param avg: boolean flag marking whether the dice __always__ rolls average,
            like NPCs and PCs on Mechano do for attack rolls.
        """
        # stats
        self.bonus = int(bonus)
        self.num_faces = list(self._parse_num_faces(num_faces))
        self.avg = avg

    def _parse_num_faces(self, num_faces: Union[int, List[int]]) -> List[int]:
        if isinstance(num_faces, list):
            return [int(i) for i in num_faces]
        elif isinstance(num_faces, int):
            return [num_faces]
        else:
            raise TypeError(f'num_faces is {type(num_faces)}')

    def base_roll(self, avg=None):
        if avg is None or self.avg is False:
            return sum(random.randint(1, num_faces) for num_faces in self.num_faces) + self.bonus
        else:
            return int((sum(self.num_faces) + len(self)) / 2)

    def roll(self, avg=None):
        return self.base_roll(avg) + self.bonus

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

        :return: string in dice notation.
        """
        def annotate(die, count):
            return f'{count}{die}' if count > 1 else f'{die}'
        dice = Counter([f'd{nf}' for nf in self.num_faces]).most_common()
        s = '+'.join([annotate(die, count) for die, count in dice])
        if self.bonus > 0:
            s += f'+{str(self.bonus)}'
        elif self.bonus < 0:
            s += f'-{str(abs(self.bonus))}'
        else:
            pass # +0
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