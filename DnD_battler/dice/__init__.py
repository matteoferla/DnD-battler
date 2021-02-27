# a generic set of dice
from .dice import Dice

# The following have heavy handed workarounds for the fact Python does not have pointers.
# namely Proficiency can be modified and affects all abilities
# an ability score/bonus can be altered thus affecting AttackRoll and SkillRoll

# an ability (str, dex, con etc.)
# a critable ability score based die
# requires Proficiency
from .ability_die import AbilityDie

# rolls that use an ability dice and behave like dice,
# but allow the ability dice to be altered.
# slightly convoluted to
from .skill_roll import SkillRoll
from .attack_roll import AttackRoll
# AttackRoll has a bound damage_dice.

# additionally
# not a die, but just the proficiency
