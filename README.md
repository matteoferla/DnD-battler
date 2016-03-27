# DnD Encounter simulator
Welcome to the D&D 5e Encounter simulator.
It was written to determine victory probabilities and to test some hypotheses.
[An online version of the simulator is hosted in Openshift](http://battle-matteoferla.rhcloud.com)

# New
The simulator relies on  creature information present in the `beastiary.csv` file. This file was kindly compiled by Jeff Fox.
It contains all creature present in the D&D 5e SDR and is distributed under the following licence:
Open Game License v 1.0a Copyright 2000, Wizards of the Coast, Inc. Copyright 2016, Wizards of the Coast, Inc.

#Documentation
This module allows the simulation of a D&D encounter.
It has three main classes:  Dice, Character, Encounter.
It also has a csv file (`beastiary.csv`) containing all 5e SDR monsters.

**Teams.** Multiple creatures of the same alignment will team up to fight creatures of different alignments in a simulation (`Encounter().battle()` for a single iteration or `Encounter().go_to_war()` for multiple).
**Gridless.** The game assumes everyone is in cotact with everyone and not on a grid. The reason being is tactics.
**Tactics.** Tactics are highly problematic both in targetting and actions to take. Players do not play as strategically as they should due to heroism and kill tallies, while the DM might play monsters really dumbly to avoid a TPK.
**Targetting.** The similator is set up as a munchkin combat where everyone targets the weakest opponent (The global variable `TARGET="enemy alive weakest"` makes the `find_weakest_target` method of the `Encounter` be used, but could be changed (unwisely) to a permutation of enemy/ally alive/dead weakest/random/fiercest.
The muchkinishness has a deleterious side-effect when the method deathmatch of the Encounter class is invoked —this allocates each Creature object in the Encounter object in a different team.
**Actions.** Action choice is dictated by turn economy. A character of a team with the greater turn economy will dodge (if it knows itself a target) or throw a net (if it has one), and so forth while a creature on the oppose side will opt for a slugfest.

```
>>> import DnD
>>> DnD.Creature('aboleth') # get from beastiary
>>> level1 = DnD.Creature("buff peseant",base='commoner',abilities = {'str': 15,'dex': 14,'con':13,'int':12,'wis':10,'cha': 8}, alignment ="good", attack_parameters='longsword') #a modified creature based off another
>>> terry=DnD.Creature("lich")
>>> terry.alignment = "good"  #the name of the alignment means only what team name they are in.  
>>> arena = DnD.Encounter(level1, 'badger')  #Encounter accepts both Creature and strings.
>>> print(arena.go_to_war(1e5) #simulate 10,000 times
>>> print(arena.battle(verbose = 1)) # simulate one encounter and tell what happens.
>>> print(DnD.Creature('tarrasque').generate_character_sheet())  #md character sheet.
>>> print(Encounter("ancient blue dragon").addmob(85).go_to_war(10))  #An ancient blue dragon is nearly a match for 85 commoners (who crit evenutally)...
```

# Class summary
## Dice
Dice accepts bonus plus an int —8 is a d8— or a list of dice —[6,6] is a 2d6— or nothing —d20.
    roll() distinguishes between a d20 and not. d20 crits have to be passed manually.
## Character
Character has a boatload of attributes. It can be initilised with a dictionary or an unpacked one... or a single name matching a preset.
## Encounter
Encounter includes the following method:
    battle(reset=1) does a single battle (after a reset of values if asked). it calls a few other fuctions such as roll_for_initiative()
    go_to_war(rounds=1000) performs many battles and gives the team results
verbosity (verbose=1) is optional. And will be hopefully be written out of the code.

There is some code messiness resulting from the unclear distinction between Encounter and Creature object, namely
a Creature interacting with another is generally a Creature method, while a Creature searching across the list of Creatures in the Encounter is an Encounter method.

There are one or two approximations that are marked `#NOT-RAW`. In the Encounter.battle method there are some thought on the action choices.



# class Creature(builtins.object)
Creature class handles the creatures and their actions and some interactions with the encounter.

Methods defined here:

TBA_act(self, verbose=0)
    # TODO

__init__(self, wildcard, **kwargs)
    Creature object creation. A lot of paramaters make a creature so a lot of assumptions are made (see __init__`).
    :param wildcard: the name of the creature.
      If nothing else is passed it will take it from the beastiary.
      If a dictionary is passed, it will process it like **kwargs,
      If a Creature object is passed it will make a copy
    :param kwargs: a lot of arguments...
    :return: a creature.
    
    The arguments are many.
    >>> print(Creature(Creature('aboleth'), ac=20).__dict__)
    `{'abilities': None, 'dex': 10, 'con_bonus': 10, 'cr': 17, 'xp': 5900, 'ac': 20, 'starting_healing_spells': 0, 'starting_hp': 135, 'condition': 'normal', 'initiative': <__main__.Dice object at 0x1022542e8>, 'str': 10, 'wis': 10, 'ability_bonuses': {'int': 0, 'cha': 0, 'dex': 0, 'con': 0, 'str': 0, 'wis': 0}, 'custom': [], 'hd': <__main__.Dice object at 0x102242c88>, 'hurtful': 36.0, 'tally': {'rounds': 0, 'hp': 0, 'battles': 0, 'hits': 0, 'damage': 0, 'healing_spells': 0, 'dead': 0, 'misses': 0}, 'hp': 135, 'proficiency': 5, 'cha_bonus': 10, 'able': 1, 'healing_spells': 0, 'copy_index': 1, 'int': 10, 'concentrating': 0, 'wis_bonus': 10, 'con': 10, 'int_bonus': 10, 'sc_ab': 'con', 'str_bonus': 10, 'level': 18, 'settings': {}, 'arena': None, 'dex_bonus': 10, 'log': '', 'cha': 10, 'dodge': 0, 'alt_attack': {'attack': None, 'name': None}, 'alignment': 'lawful evil ', 'attacks': [{'attack': <__main__.Dice object at 0x1022545f8>, 'damage': <__main__.Dice object at 0x1022545c0>, 'name': 'tentacle'}, {'attack': <__main__.Dice object at 0x102254668>, 'damage': <__main__.Dice object at 0x102254630>, 'name': 'tentacle'}, {'attack': <__main__.Dice object at 0x1022546d8>, 'damage': <__main__.Dice object at 0x1022546a0>, 'name': 'tentacle'}], 'attack_parameters': [['tentacle', 9, 5, 6, 6], ['tentacle', 9, 5, 6, 6], ['tentacle', 9, 5, 6, 6]], 'buff_spells': 0, 'temp': 0, 'name': 'aboleth'}`

__str__(self)
    Return str(self).

act(self, verbose=0)

assess_wounded(self, verbose=0)

cast_barkskin(self)

cast_healing(self, weakling, verbose=0)

cast_nothing(self, state='activate')

check_action(self, action, verbose)
    # TODO

check_advantage(self, opponent)

copy(self)
    :return: a copy of the creature.

do_action(self, action, verbose)
    # TODO

generate_character_sheet(self)
    An markdown character sheet.
    :return: a string

heal(self, points, verbose=0)

isalive(self)

multiattack(self, verbose=0, assess=0)

net(self, opponent, verbose=0)

ready(self)

reset(self)

set_level(self, level=None)
    Alter the level of the creature.
    :param level: opt. int, the level. if absent it will set it to the stored level.
    :return: nothing. changes self.

take_damage(self, points, verbose=0)

----------------------------------------------------------------------
Static methods defined here:

clean_settings(dirtydex)
    Sanify the settings
    :return: a cleaned dictionary

----------------------------------------------------------------------
Data descriptors defined here:

__dict__
    dictionary for instance variables (if defined)

__weakref__
    list of weak references to the object (if defined)

----------------------------------------------------------------------
Data and other attributes defined here:

ability_names = ['str', 'dex', 'con', 'wis', 'int', 'cha']

beastiary = {'aboleth': {'AB_Cha': '4', 'AB_Con': '0', 'AB_Dex': '0', ...
    
# class Dice(builtins.object)
Methods defined here:

__init__(self, bonus=0, dice=20, avg=False, twinned=None, role='ability')
    Class to handle dice and dice rolls
    :param bonus: int, the bonus added to the attack roll
    :param dice: list of int, the dice size.
    :param avg: boolean flag marking whether the dice always rolls average, like NPCs and PCs on Mechano do for attack rolls.
    :param twinned: a dice. ja. ehrm. this is the other dice. The crits are passed to it. It should be a weak ref or the crits passed more pythonically.
    :param role: string, but actually on a restricted vocabulary: ability, damage, hd or healing. Extras can be added, but they won't trigger some things
    :return: a rollable dice!
    
    The parameters are set to attributes. Other attributes are:
    * critable: determined from `role` attribute
    * cirt: 0 or 1 ... or more if you want to go 3.5 and crit train.
    * advantage: trinary int. -1 is disadvantage, 0 normal, 1 is advantage.

__str__(self)
    This is rather inelegant piece of code and is not overly flexible. If the dice fail to show, they will still work.
    :return: string in dice notation.

icosaroll(self, verbose=0)
    A roll that is a d20. It rolls advantage and disadvatage and calls `_critcheck`.
    :param verbose:
    :return:

multiroll(self, verbose=0)
    A roll that is not a d20. It adds the bonus and rolls (x2 if a crit).
    :param verbose:
    :return:

roll(self, verbose=0)
    The roll method, which calls either icosaroll or multiroll.
    :param verbose: debug
    :return: the value rolled (and alters the dice too if need be)
    
# class Encounter(builtins.object)
In a dimentionless model, move action and the main actions dash, disengage, hide, shove back/aside, tumble and overrun are meaningless.
weapon attack —default
two-weapon attack —
    Good when the opponent has low AC (<12) if 2nd attack is without proficiency.
    Stacks with bonuses such as sneak attack or poisoned weapons —neither are in the model.
    Due to the 1 action for donning/doffing a shield, switch to two handed is valid for unshielded folk only.
    Best keep two weapon fighting as a prebuild not a combat switch.
AoE spell attack — Layout…
targetted spell attack —produce flame is a cantrip so could be written up as a weapon. The bigger ones. Spell slots need to be re-written.
spell buff —Barkskin is a druidic imperative. Haste? Too much complication.
spell debuff —Bane…
dodge —targetted and turn economy
help —high AC target (>18), turn economy, beefcake ally
ready —teamwork preplanning. No way.
grapple/climb —very situational. grapple/shove combo or barring somatic.
disarm —disarm… grey rules about whether picking it up or kicking it away is an interact/move/bonus/main action.
    netting is a better option albeit a build.
called shot —not an official rule. Turn economy.

Methods defined here:

__add__(self, other)

__getitem__(self, item)

__init__(self, *lineup)
    Initialize self.  See help(type(self)) for accurate signature.

__iter__(self)

__len__(self)

__str__(self)
    Return str(self).

addmob(self, n)

append(self, newbie)

battle(self, reset=1, verbose=1)

check(self)

extend(self, iterable)

find(self, what, searcher=None, team=None)

go_to_war(self, rounds=1000)

json(self)

predict(self)

reset(self)

roll_for_initiative(self, verbose=0)

set_deathmatch(self)


----------------------------------------------------------------------
Data and other attributes defined here:

Victory = <class 'DnD_Battler.Encounter.Victory'>
    The way the encounter ends is a victory error is raised to stop the creatures from acting further.



