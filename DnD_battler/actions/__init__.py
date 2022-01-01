"""
It is a double cyclic reference, but it is the best way to prep the code for ML.
Namely, a Creature has a list of Attack objects, which have a reference to the Creature...
"""

from .enums import AttackType, TargetChoice
from .errors import *
from .action import Action
from .melee import MeleeAttack
from .multiattack import Multiattack
from .armory import *