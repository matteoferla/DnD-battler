# DnD-battler
A 5e D&amp;D battle simulator written for my own amusement to test some hypotheses.
Edit: [An online version of the simulator is hosted in Openshift](battle-matteoferla.rhcloud.com)
Edit: I started making a spreadsheet of a beastiary, which I was hoping to use to get all the presets that are currently hardcoded, but I have run out of time for now to do them all.
The code nevertheless if give only a string to initialise a Creature it will check in both. Disclaimer based on my vague legal knowledge, download the spreadsheet only if you own the MM.

```import DnD_battler as DnD
DnD.Creature("barkskin_bear")  ###A criptic hardcoded creature
DnD.Creature("hobgoblin")  ##A creature from the beastiary spreadsheet
```

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
