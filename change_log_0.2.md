## Split up

The file DnD.py was over 1,600 lines long.
I wrote it back in 2015 as practice while switching from Perl to Python.
Now it has been split up properly.

## Dice

* `Dice().dice` changed to `Dice().num_faces`.
* `from_notation` created.
* TODO crit and advantage are handled so weirdly.


## Encounter

* Victory moved out.

## Creature

By having a faux-overloaded init method it was overly complicated. I have split it up to keep it simple.

* finess and monks wis to ac, should be coded.
* TODO: add proficiency_bonus where required.