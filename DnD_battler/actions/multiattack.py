from .action import Action
from typing import *

class Multiattack(Action):
    """
    The case where a creature has a choice of 2 A actions and 1 B action or 1 A, 1 B or 1 C]
    need to be coded as separate actions.
    """

    def __init__(self,
                 creature,
                 name: str,
                 actions: List[Action],
                 **kwargs):
        super().__init__(creature=creature, name=name, typology=AttackType.melee,  **kwargs)
        self.actions = actions

    def do(self):
        for action in self.actions:
            action.do()

    def absolute_score(self):
        return sum([action.absolute_score() for action in self.actions])

    def score(self) -> float:
        return sum([action.score() for action in self.actions])