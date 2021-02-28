__doc__ = """
This module allows the simulation of a D&D encounter.
It has three main classes:  Dice, Character, Encounter.
It also has a csv file (`beastiary.csv`) containing all 5e SDR monsters.

**Teams.** Multiple creatures of the same alignment will team up to fight creatures of different alignments in a simulation (`Encounter().battle()` for a single iteration or `Encounter().go_to_war()` for multiple).
**Gridless.** The game assumes everyone is in cotact with everyone and not on a grid. The reason being is tactics.
**Tactics.** Tactics are highly problematic both in targetting and actions to take. Players do not play as strategically as they should due to heroism and kill tallies, while the DM might play monsters really dumbly to avoid a TPK.
**Targetting.** The similator is set up as a munchkin combat where everyone targets the weakest opponent (The class variable `self.target="enemy alive weakest"` makes the `find_weakest_target` method of the `Encounter` be used, but could be changed (unwisely) to a permutation of enemy/ally alive/dead weakest/random/fiercest.
The muchkinishness has a deleterious side-effect when the method deathmatch of the Encounter class is invoked —this allocates each Creature object in the Encounter object in a different team.
**Actions.** Action choice is dictated by turn economy. A character of a team with the greater turn economy will dodge (if it knows itself a target) or throw a net (if it has one), and so forth while a creature on the oppose side will opt for a slugfest.


# Example uses

    >>> import DnD_battler
    >>> DnD_battler.Creature('aboleth') # get from beastiary
    >>> level1 = DnD_battler.Creature("buff peseant",base='commoner',abilities = {'str': 15,'dex': 14,'con':13,'int':12,'wis':10,'cha': 8}, alignment ="good", attack_parameters='longsword') #a modified creature based off another
    >>> arena = DnD_battler.Encounter(level1, 'badger')  #Encounter accepts both Creature and strings.
    >>> print(arena.go_to_war(1e5) #simulate 10,000 times
    >>> print(arena.battle()) # simulate one encounter and tell what happens.
    >>> print(DnD_battler.Creature('tarrasque').generate_character_sheet())  #md character sheet.
    >>> print(Encounter("ancient blue dragon").addmob(85).go_to_war(10))  #An ancient blue dragon is nearly a match for 85 commoners (who crit evenutally)...

# Class summary
## Dice
Dice accepts bonus plus an int —8 is a d8— or a list of dice —[6,6] is a 2d6— or nothing —d20.
    roll() distinguishes between a d20 and not. d20 crits have to be passed manually.
## Character
Character has a boatload of attributes. It can be initilised with a dictionary or an unpacked one... or a single name matching a preset.
## Encounter
Encounter includes the following method:
    battle(reset=1) does a single battle (after a reset of values if asked). it calls a few other fuctions such as roll_for_initiative()
    go_to_war(rounds=1000) performs many battles and gives the team results.

There is some code messiness resulting from the unclear distinction between Encounter and Creature object, namely
a Creature interacting with another is generally a Creature method, while a Creature searching across the list of Creatures in the Encounter is an Encounter method.

There are one or two approximations that are marked #NOT-RAW. In the Encounter.battle method there are some thought on the action choices.
"""