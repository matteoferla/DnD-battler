# DnD-battler
A 5e D&amp;D encounter simulator written to determine victory probabilities and to test some hypotheses.
[An online version of the simulator is hosted in Openshift](http://battle-matteoferla.rhcloud.com)

# New
The simulator relies on  creature information present in the `beastiary.csv` file. This file was kindly compiled by Jeff Fox.
It contains all creature present in the D&D 5e SDR and is distributed under the following licence:
Open Game License v 1.0a Copyright 2000, Wizards of the Coast, Inc. Copyright 2016, Wizards of the Coast, Inc. 
This f.

#Documentation
Welcome to the D&D Battle simulator.
Go to the § HERE IS WHERE YOU CAN DECIDE THE LINE UP if you want to try it out.
The similator is set up as a munchkin combat where everyone targets the weakest due to find_weakest_target method of the Encounter class.
Changing TARGET (above) to something else will change the targetting.
The muchkinishness has a deleterious side-effect when the method deathmatch of the Encounter class is invoked —this allocates each Creature object in the Encounter object in a different team.
The nitty-gritty:
There are three classes he=re: Dice, Character, Encounter.
Dice accepts bonus plus an int —8 is a d8— or a list of dice —[6,6] is a 2d6— or nothing —d20.
    roll() distinguishes between a d20 and not. d20 crits have to be passed manually.
Character has a boatload of attributes. It can be initilised with a dictionary or an unpacked one... or a single name matching a preset.
Encounter includes the following method:
    battle(reset=1) does a single battle (after a reset of values if asked). it calls a few other fuctions such as roll_for_initiative()
    go_to_war(rounds=1000) performs many battles and gives the team results
verbosity (verbose=1) is optional.
There is some code messiness resulting from the unclear distinction between Encounter and Creature object, namely
a Creature interacting with another is generally a Creature method, while a Creature searching across the list of Creatures in the Encounter is an Encounter method.
There are one or two approximations that are marked #NOT-RAW. In the Encounter.battle method there are some thought on the action choices.

# Example usage
```
import DnD_battler as DnD
#make creature
terry=DnD.Creature("tarrasque")  ##A creature from the beastiary spreadsheet
terry.alignment="good"
#make encounter (a collection of creatures), which can either be a Creature instance or a string (Creature instance created)
print(DnD.Encounter(terry,"tarrasque").go_to_war(1000))
#add commoners
print(Encounter(Creature("ancient blue dragon")).addmob(200).go_to_war(10))
```