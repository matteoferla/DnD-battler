## Split up

The file DnD.py was over 1,600 lines long.
I wrote it back in 2015 as practice while switching from Perl to Python.
Now it has been split up properly.

## Dice

* `Dice` has been split
* `Dice().dice` changed to `Dice().num_faces`.
* `from_notation` created.

`Dice` was overly convoluted because it was an all-in-one for no reason. These are the new classes:

* `Dice` is just regular dice roll, say for damage etc.
* `Ability` extends `Dice` holds the ability score of a character and there is meant to be one per ability and all derived skills use
    this meaning that it can change and affect all. It requires a `Proficiency` instance
* `SkillRoll` pretends to inherit ability but is a wrapper for it. It allows modifiers to be added. 
    Say a +2 for history check would be added to the ability bonus and proficiency only for a history check.
    Optionally, checks for crits and handles advantage/disadvantage.
* `AttackRoll` extends SkillRoll and holds attack dice too. `attack` rolls against an AC value and rolls for damage


## Creature

By having a faux-overloaded init method it was overly complicated. I have split it up to keep it simple and tidier.

The init constructor does not use a creature from the monster manual, while the `load(creature_name)` does.
A blank creature is basically a commoner, so these ought to be the same:

```python
from DnD_battler import Creature
Creature()
Creature.load('commoner')
```
Both accept several arguments. 

```python
from DnD_battler import Creature
Creature(name="Achilles", alignment='Achaeans')
Creature.load(creature_name='commoner', name="Achilles", alignment='Achaeans')
```

The `.proficiency.bonus` is handled already in a SkillRoll or AttackRoll.
The `.attacks` is a list of `AttackRolls`.
The `.ac` dynamic attribute actually returns `.armor.ac`. Which handles the AC calculations
which are based on one or more ability dice (generally `.dex`, but monks add `.dex` and `.wis`).
The dice are not rolled, they are solely used to get the common ability bonus
(and `temp_modifier` and `proficiency.bonus`).

## Encounter

* Victory moved out.
* Encounter accepts only Creatures, not creature names*.

(*) Sure, I have removed few overloaded alternative options, which albeit good for lazier coding may result 
in unneeded complication.

## TODO

* Spellcasting is not reinstated
* Location, weapon types (range or melee)
* Decision-making needs to be changed so each option is given a score and by multiplying by a weight vector
    gives the most preferred option. The vector would be manually determined for now... but these are basically
    hyperparamters for machine learning 