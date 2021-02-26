## Split up

The file DnD.py was over 1,600 lines long.
I wrote it back in 2015 as practice while switching from Perl to Python.
Now it has been split up properly.

## Dice

* `Dice().dice` changed to `Dice().num_faces`.
* `from_notation` created.
* TODO invert num_faces and bonus!

## Encounter

* Victory moved out.

## Creature