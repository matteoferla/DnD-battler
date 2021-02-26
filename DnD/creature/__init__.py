from ._adv_base import CreatureAdvBase
from ._utils import CreatureUtils
from ._action import CreatureAction
import warnings, math

class Creature(CreatureAdvBase, CreatureUtils, CreatureAction):
    """
    Creature class handles the creatures and their actions and some interactions with the encounter.
    """

    def copy(self):
        """
        :return: a copy of the creature. with an altered name.
        """
        self.copy_index += 1
        return Creature(self, name=self.name + ' ' + str(self.copy_index))


    def isalive(self):
        if self.hp > 0: return 1

    def take_damage(self, points, verbose=0):
        self.hp -= points
        if verbose: verbose.append(self.name + ' took ' + str(points) + ' of damage. Now on ' + str(self.hp) + ' hp.')
        if self.concentrating:
            dc = points / 2
            if dc < 10: dc = 10
            if self[self.sc_ab].roll() < dc:
                self.conc_fx()
                if verbose: verbose.append(self.name + ' has lost their concentration')