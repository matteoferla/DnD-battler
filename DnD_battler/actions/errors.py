from typing import *

class Victory(Exception):
    """
    The way the encounter ends is a victory error is raised to stop the creatures from acting further.
    """
    pass

class ActionError(Exception):
    """
    The attempted action could not be done.
    """
    def __init__(self, message: Optional[str]=None):
        if message is None:
            message = 'The attempted action could not be done.'
        super().__init__(message)

class AttackRangeError(ActionError):
    """
    The attempted attack could not be done.
    """
    def __init__(self, range: int, limit: int):
        self.range = range
        self.limit = limit
        super().__init__(f'The attack is out of range (range: {self.range} ft, limit: {self.limit}) ft')


class SpellSlotsError(ActionError):
    """
    There are no spellslots left
    """
    def __init__(self):
        super().__init__(f'There are no spellslots left')

class ConcentrationError(ActionError):
    """
    Creature is already concentrating
    """

    def __init__(self):
        super().__init__(f'Creature is already concentrating')