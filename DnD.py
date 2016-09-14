# -*- coding: UTF-8 -*-
__author__ = "Matteo"
__copyright__ = "Don't blame me for a TPK"
__email__ = "matteo.ferla on the gmail"
__date__ = '23/08/15'

import random
import math
import warnings

#N="\n"
N = "<br/>"
TARGET = 'enemy alive weakest'
# target='enemy alive weakest', target='enemy alive random', target='enemy alive fiersomest'


"""
This module allows the simulation of a D&D encounter.
It has three main classes:  Dice, Character, Encounter.
It also has a csv file (`beastiary.csv`) containing all 5e SDR monsters.

**Teams.** Multiple creatures of the same alignment will team up to fight creatures of different alignments in a simulation (`Encounter().battle()` for a single iteration or `Encounter().go_to_war()` for multiple).
**Gridless.** The game assumes everyone is in cotact with everyone and not on a grid. The reason being is tactics.
**Tactics.** Tactics are highly problematic both in targetting and actions to take. Players do not play as strategically as they should due to heroism and kill tallies, while the DM might play monsters really dumbly to avoid a TPK.
**Targetting.** The similator is set up as a munchkin combat where everyone targets the weakest opponent (The global variable `TARGET="enemy alive weakest"` makes the `find_weakest_target` method of the `Encounter` be used, but could be changed (unwisely) to a permutation of enemy/ally alive/dead weakest/random/fiercest.
The muchkinishness has a deleterious side-effect when the method deathmatch of the Encounter class is invoked —this allocates each Creature object in the Encounter object in a different team.
**Actions.** Action choice is dictated by turn economy. A character of a team with the greater turn economy will dodge (if it knows itself a target) or throw a net (if it has one), and so forth while a creature on the oppose side will opt for a slugfest.


# Example uses

    >>> import DnD_Battler.py as DnD
    >>> DnD.Creature('aboleth') # get from beastiary
    >>> level1 = DnD.Creature("buff peseant",base='commoner',abilities = {'str': 15,'dex': 14,'con':13,'int':12,'wis':10,'cha': 8}, alignment ="good", attack_parameters='longsword') #a modified creature based off another
    >>> arena = DnD.Encounter(level1, 'badger')  #Encounter accepts both Creature and strings.
    >>> print(arena.go_to_war(1e5) #simulate 10,000 times
    >>> print(arena.battle(verbose = 1)) # simulate one encounter and tell what happens.
    >>> print(DnD.Creature('tarrasque').generate_character_sheet())  #md character sheet.
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
    go_to_war(rounds=1000) performs many battles and gives the team results
verbosity (verbose=1) is optional. And will be hopefully be written out of the code.

There is some code messiness resulting from the unclear distinction between Encounter and Creature object, namely
a Creature interacting with another is generally a Creature method, while a Creature searching across the list of Creatures in the Encounter is an Encounter method.

There are one or two approximations that are marked #NOT-RAW. In the Encounter.battle method there are some thought on the action choices.
"""


######################DICE######################
class Dice:
    def __init__(self, bonus=0, dice=20, avg=False, twinned=None, role="ability"):
        """
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
        """
        if twinned:
            self.twinned = twinned
        else:
            self.twinned = None
        ##Can it crit?
        self.role = role
        if self.role == "damage" or self.role == "healing" or self.role == "hd":
            self.critable = 0
        else:
            self.critable = 1

        # stats
        self.bonus = int(bonus)
        if type(dice) is list:
            self.dice = dice
        elif type(dice) is str:
            raise Exception("str is not yet supported as dice type")  # TODO add support of d6 notation
        else:
            self.dice = [dice]
        self.advantage = 0
        self.crit = 0  # multiplier+1. Actually you can't get a crit train anymore.
        self.avg = avg

    def __str__(self):
        """
        This is rather inelegant piece of code and is not overly flexible. If the dice fail to show, they will still work.
        :return: string in dice notation.
        """
        s = ''
        if len(self.dice) == 1:
            s += 'd' + str(self.dice[0]) + '+'
        elif len(self.dice) == 2 and self.dice[0] == self.dice[1]:
            s += '2d' + str(self.dice[0]) + '+'
        elif len(self.dice) == 2 and self.dice[0] != self.dice[1]:
            s += 'd' + str(self.dice[0]) + '+d' + 'd' + str(self.dice[1]) + '+'
        elif len(self.dice) == 3 and self.dice[0] == self.dice[1] == self.dice[1]:
            s += '3d' + str(self.dice[0]) + '+'
        elif len(self.dice) == 3 and self.dice[0] != self.dice[1]:
            s += 'd' + str(self.dice[0]) + '+d' + str(self.dice[1]) + '+d' + str(self.dice[1]) + '+'
        else:
            for x in range(len(self.dice)):
                s += 'd' + str(self.dice[x]) + '+'
        s += str(self.bonus)
        return s

    def multiroll(self, verbose=0):
        """
        A roll that is not a d20. It adds the bonus and rolls (x2 if a crit).
        :param verbose:
        :return:
        """
        result = self.bonus
        for d in self.dice:
            if self.avg:  # NPC rolls
                if self.crit:
                    result += d
                else:
                    result += round(d / 2 + 1)
            else:
                for x in range(0, self.crit + 1): result += random.randint(1, d)
        self.crit = 0
        return result

    def icosaroll(self, verbose=0):
        """
        A roll that is a d20. It rolls advantage and disadvatage and calls `_critcheck`.
        :param verbose:
        :return:
        """
        self.crit = 0
        if self.advantage == 0:
            return self._crit_check(random.randint(1, 20), verbose) + self.bonus
        elif self.advantage == -1:  # AKA disadvatage
            return self._crit_check(sorted([random.randint(1, 20), random.randint(1, 20)])[0], verbose) + self.bonus
        elif self.advantage == 1:
            return self._crit_check(sorted([random.randint(1, 20), random.randint(1, 20)])[1], verbose) + self.bonus

    def _crit_check(self, result, verbose=0):
        """
        Checks if the dice is a crit.
        :param result: dice roll result.
        :param verbose: a debug paramater that I really ought to write out of the code.
        :return: alters the dice roll to -999 if a crit fail or 999 and adds a crit marker to the twinned dice (_i.e._ the attack dice)
        """
        if not self.critable:
            print("DEBUG: A crit check was called on an uncritable roll ", self.role)
            return result
        elif result == 1:
            if verbose: verbose.append("Fumble!")
            return -999  # automatic fail
        elif result == 20:
            if verbose: verbose.append("Crit!")
            if self.twinned: self.twinned.crit = 1
            return 999  # automatic hit.
        else:
            return result

    def roll(self, verbose=0):  # THIS ASSUMES NO WEAPON DOES d20 DAMAGE!! Dragonstar and Siege engines don't.
        """
        The roll method, which calls either icosaroll or multiroll.
        :param verbose: debug
        :return: the value rolled (and alters the dice too if need be)
        """
        if not self.dice:
            raise Exception('A non-existant dice has been attempted to be rolled')
        # elif self.dice[0] == 20:
        elif self.critable:  # the problem is crits and adv and only d20 can. Nothing deals d20 damage, but someone might try.
            return self.icosaroll(verbose)
        else:
            return self.multiroll(verbose)


######################CREATURE######################

class Creature:
    """
    Creature class handles the creatures and their actions and some interactions with the encounter.
    """

    @staticmethod
    def load_beastiary(path):
        """
        `load_beastiary(path)` (formerly just `_beastiary`) is a function while beastiary is the attribute it fills.

        There are a few way of how the creature data comes about. This is to initialise the beastiary, now the standard source of beastiary.

        When the code starts, it tries first to find a `beastiary.csv` file.
        It's a method because it can fail and needs to be rerun in case there is no `beastiary.csv`.
        :param path: the string to the csv file
        :return: the beastiary, a dictionary (keys: creature names) of dictionary (keys: csv headers)
        The headers of the csv are: (some are for analysis, _e.g._ `hp_fudge`)
        * name (becomes the key too)
        * alt
        * alignment
        * type
        * size
        * armour_name
        * stated_ac
        * armor_bonus
        * ac
        * stated_hp
        * hp
        * expected_hp
        * hp_fudge
        * level
        * hd
        * Str
        * Dex
        * Con
        * Int
        * Wis
        * Cha
        * attack_parameters
        * CR
        * xp
        * regen
        * healing_spells
        * healing_dice
        * healing_bonus
        * sc_ability
        * log
        * proficiency
        * initiative_bonus
        * AB_Str   -- as in ability bonus.
        * AB_Dex
        * AB_Con
        * AB_Int
        * AB_Wis
        * AB_Cha
        """
        try:
            import csv
            r = csv.reader(open(path, encoding='utf-8'))
            headers = next(r)
            beastiary = {}
            for line in r:
                beast = {h: line[i] for i, h in enumerate(headers) if line[i]}
                if 'name' in beast:
                    beastiary[beast['name']] = beast
            return beastiary
        except Exception as e:
            warnings.warn('Beastiary error, expected path ' + path + ' error ' + str(e))
            return {}

    beastiary = load_beastiary.__func__('beastiary.csv')
    ability_names = ['str', 'dex', 'con', 'wis', 'int', 'cha']

    def __init__(self, wildcard, **kwargs):  # I removed *args... not sure what they did.
        """
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
        """
        self.log = ""
        if not kwargs and type(wildcard) is str:
            self._fill_from_beastiary(wildcard)
        elif type(wildcard) is dict:
            self._fill_from_dict(wildcard)
            if not kwargs == {}:
                print("dictionary passed followed by unpacked dictionary error")
        elif kwargs and type(wildcard) is str:
            if wildcard in self.beastiary:
                self._initialise(base=wildcard, **kwargs)
            else:
                self._initialise(name=wildcard, **kwargs)
        elif type(wildcard) is Creature:
            self._initialise(base=wildcard, **kwargs)
        else:
            warnings.warn("UNKNOWN COMBATTANT:" + str(wildcard))
            # raise Exception
            print("I will not raise an error. I will raise Cthulhu to punish this user errors")
            self._fill_from_preset("cthulhu")

    def _initialise(self, **settings):
        """`
        Preface.
        Character creation in DnD is rather painful. Here due to missing it is even more complex.
        Also, creature, character and monster are used interchangably here unfortunately, which will be fixed one day.
        The method _set

        This is the order of creation. All attributes are in lowercase regardless of the style on the PHB.
        1. a creature can be based off another, if the `base attribute is set`(str or Creature).
        2. set `name`
        3. set `level` (def 1)
        4. set `xp` (def None)
        5. set `proficiency` (proficiency bonus), 1 + round(self.level / 4) if absent, but will be overidden if hp is not specified as the `set_level` will generate it from HD and level
        6. set ability bonues (`_initialise_abilities` method). To let the user give a base creature and weak a single ability (__e.g.__ `Creature('Commoner',name='mutant commoner', str=20)), the creature has abilities as individual attributes with three letter codes, __e.g.__ `self.str` and as a dictionary (`self.abilities`), while `self.ability_bonuses` has a twin that is the suffix `_bonus` (__e.g.__ `self.str_bonus`).
        7. set `hp`
        8. AC (`self.ac`)
        9. spellcasting (complex, may change in future): `sc_ab` the spellcasting ability as three char str,
        10. `initiative_bonus`
        11. combat stats... attack_parameters=[['rapier', 4, 2, 8]], alt_attack=['net', 4, 0, 0]

        name, alignment="good", ac=10, initiative_bonus=None, hp=None, attack_parameters=[['club', 2, 0, 4]],
                 alt_attack=['none', 0],
                 healing_spells=0, healing_dice=4, healing_bonus=None, ability_bonuses=[0, 0, 0, 0, 0, 0], sc_ability='wis',
                 buff='cast_nothing', buff_spells=0, log=None, xp=0, hd=6, level=1, proficiency=2
                 """

        if settings:
            self.settings = Creature.clean_settings(settings)
        else:
            self._fill_from_preset('commoner')  # or Cthulhu?
            print("EMPTY CREATURE GIVEN. SETTING TO COMMONER")
            return 0

        # Mod of preexisting
        if 'base' in self.settings:
            #Sanify first and make victim
            if type(self.settings['base']) is str:
                victim = Creature(
                    self.settings['base'])  # generate a preset and get its attributes. Seems a bit wasteful.
            elif type(self.settings['base']) is Creature:
                victim = self.settings['base']
            else:
                raise TypeError
            #copy all
            #victim.ability_bonuses #in case the user provided with ability scores, which are overridden by adbility bonues
            base = {x: getattr(victim, x) for x in dir(victim) if getattr(victim, x) and x.find("__") == -1 and x.find("_") != 0 and x != 'beastiary'}
            base['ability_bonuses']={}
            #base.update(**self.settings)
            for (k,v) in self.settings.items():
                if type(v) is dict:
                    base[k].update(v)
                else:
                    base[k] = v
            self.settings = base

        # Name etc.
        self._set('name', 'nameless')
        self._set('level', 0, 'int')
        self._set('xp', None, 'int')

        # proficiency. Will be overridden if not hp is provided.
        self._set('proficiency', 1 + round(self.level / 4))  # TODO check maths on PH

        # set abilities
        self._initialise_abilities()

        # Get HD
        self.hd = None
        if 'hd' in self.settings.keys():
            if type(self.settings['hd']) is Dice:
                self.hd = self.settings['hd']  # we're dealing with a copy of a beastiary obj.
            else:
                self.hd = Dice(self.ability_bonuses['con'], int(self.settings['hd']), avg=True, role="hd")
        elif 'size' in self.settings.keys():
            size_cat = {"small": 6, "medium": 8, "large": 10, "huge": 12}
            if self.settings['size'] in size_cat.keys():
                self.hd = Dice(self.ability_bonuses['con'], size_cat[self.settings['size']], avg=True, role="hd")
        elif 'hp' in self.settings and 'level' in self.settings:
            #Guess based on hp and level. It is not that dodgy really as the manual does not use odd dice.
            # hp =approx. 0.5 HD * (level-1) + HD + con * level
            # HD * (0.5* (level-1)+1) = hp - con*level
            # HD = (hp - con*level)/(level+1)
            bestchoice=(int(self.settings['hp'])-int(self.ability_bonuses['con']) * int(self.settings['level']))/((int(self.settings['level'])+1))
            print(int(self.settings['hp']),int(self.ability_bonuses['con']), int(self.settings['level']))
            print("choice HD...",bestchoice)
            #print("diagnosis...",self.ability_bonuses)
            warnings.warn('Unfinished case to guess HD. so Defaulting hit dice to d8 instead') #TODO finish
            self.hd = Dice(self.ability_bonuses['con'], 8, avg=True, role="hd")
        else:
            #defaulting to d8
            warnings.warn('Insufficient info: defaulting hit dice to d8')
            self.hd = Dice(self.ability_bonuses['con'], 8, avg=True, role="hd")

        # Get HP
        if 'hp' in self.settings.keys():
            self.hp = int(self.settings['hp'])
            self.starting_hp = self.hp
        elif self.settings['level']:
            self.set_level()
        else:
            raise Exception('Cannot make character without hp or hd + level provided')

        # AC
        if not 'ac' in self.settings.keys():
            self.settings['ac'] = 10 + self.ability_bonuses['dex']
        self.ac = int(self.settings['ac'])

        # init
        if not 'initiative_bonus' in self.settings:
            self.settings['initiative_bonus'] = self.ability_bonuses['dex']
        self.initiative = Dice(int(self.settings['initiative_bonus']), 20, role="initiative")

        ##spell casting ability_bonuses
        if 'sc_ability' in self.settings:
            self.sc_ab = self.settings['sc_ability'].lower()
        elif 'healing_spells' in self.settings or 'buff_spells' in self.settings:
            self.sc_ab = max('wis', 'int', 'cha',
                             key=lambda ab: self.ability_bonuses[ab])  # Going for highest. seriously?!
            print(
                "Please specify spellcasting ability of " + self.name + " next time, this time " + self.sc_ab + " was used as it was biggest.")
        else:
            self.sc_ab = 'con'  # TODO fix this botch up.
        if not 'healing_bonus' in self.settings:
            self.settings['healing_bonus'] = self.ability_bonuses[self.sc_ab]
        if 'healing_spells' in self.settings:
            self.starting_healing_spells = int(self.settings['healing_spells'])
            self.healing_spells = self.starting_healing_spells
            if not 'healing_dice' in self.settings:
                self.settings['healing_dice'] = 4  # healing word.
            self.healing = Dice(int(self.settings['healing_bonus']), int(self.settings['healing_dice']),
                                role="healing")  ##Healing dice can't crit or have adv.
        else:
            self.starting_healing_spells = 0
            self.healing_spells = 0
            # not a healer

        # attacks
        self.attacks = []
        self.hurtful = 0
        if not 'attack_parameters' in self.settings:
            # Benefit of doubt. Given 'em a dagger .
            self.settings['attack_parameters'] = 'dagger'
        if type(self.settings['attack_parameters']) is str:
            try:
                import json
                x = json.loads(self.settings['attack_parameters'].replace("*", "\""))
                self._attack_parse(x)
                self.attack_parameters = x
            except:
                #These have to be readable by _attack_parse
                weapons = {'club': 4, 'greatclub':8,
                           'dagger': 4, 'shortsword': 6, 'longsword': 8, 'bastardsword': 10, 'greatsword': 12,
                           'rapier': 8, 'scimitar': 6, 'sickle':4,
                           'handaxe':6, 'battleaxe':8, 'waraxe':10,'greataxe':12,
                           'javelin':6, 'spear':6, 'flail':8, 'glaive':10, 'halberd':10, 'lance':12, 'pike':10, 'trident': 6,
                           'war pick':8,
                           'lighthammer':4, 'mace':6, 'warhammer':8,
                           'quaterstaff':6, 'morningstar':8, 'punch':1, 'whip':4} #parsing of strings for dice not implemented yet, so punch is d1 for now.
                # TODO weapons removed as they gave trouble:
                #'maul':[6,6],
                # 'brütal war pick': [8, 8],  # okay, I could not resist it.

                #bastard sword and war axe are no more due to the versatile rule, however they were kept here to keep it simple
                #ranged weapons are missing for now...
                for w in weapons.keys():
                    if self.settings['attack_parameters'].lower().find(w) > -1:
                        # TODO fix the fact that a it gives the finesse option to all.
                        chosen_ab = self.ability_bonuses[max('str', 'dex', key=lambda ab: self.ability_bonuses[ab])]
                        self.attack_parameters = [[w, self.proficiency + chosen_ab, chosen_ab, weapons[w]]]
                        self._attack_parse(self.attack_parameters)
                        self.log += "Weapon matched by str to " + w + N
                        break
                else:
                    raise Exception("Cannot figure out what is: " + self.settings['attack_parameters'] + str(
                        type(self.settings['attack_parameters'])))
        elif type(self.settings['attack_parameters']) is list:
            self.attack_parameters = self.settings['attack_parameters']
            self._attack_parse(self.attack_parameters)
        else:
            raise Exception('Could not determine weapon')
        ##Weird bit needing upgrade.
        if 'alt_attack' in self.settings and type(self.settings['alt_attack']) is list:
            self.alt_attack = {'name': self.settings['alt_attack'][0],
                               'attack': Dice(self.settings['alt_attack'][1], 20)}  # CURRENTLY ONLY NETTING IS OPTION!
        else:
            self.alt_attack = {'name': None, 'attack': None}
        # last but not least
        if 'alignment' not in self.settings:
            self.settings['alignment'] = "unassigned mercenaries"  # hahaha!
        self.alignment = self.settings['alignment']
        # internal stuff
        self.tally = {'damage': 0, 'hits': 0, 'dead': 0, 'misses': 0, 'battles': 0, 'rounds': 0, 'hp': 0,
                      'healing_spells': 0}
        self.copy_index = 1
        self.condition = 'normal'

        self.dodge = 0
        self.concentrating = 0
        self.temp = 0

        self.buff_spells = None
        if 'buff_spells' in self.settings:
            self.buff_spells = int(self.settings['buff_spells'])
            self.conc_fx = getattr(self, self.settings['buff'])
        else:
            self.buff_spells = 0

        if 'cr' in self.settings:
            self.cr = self.settings['cr']
        elif 'level' in self.settings:
            # TODO check maths on MM.
            if int(self.settings['level']) > 1:
                self.cr = int(self.settings['level']) - 1
            else:
                self.cr = 0.5
        else:
            self.cr = None  # vermin

        ##backdoor and overider
        self._set('custom', [])
        for other in self.custom:
            if other == "conc_fx":
                getattr(self, self.settings['conc_fx'])
            else:
                self._set(other)

        self.arena = None
        self.settings = {}

    @staticmethod
    def clean_settings(dirtydex):
        """
        Sanify the settings
        :return: a cleaned dictionary
        """
        ability_names=['str', 'dex', 'con', 'wis', 'int', 'cha']
        #lowercase
        lowerdex = {k.lower(): dirtydex[k] for k in dirtydex}

        #sort issue with abilities
        cleandex = {'abilities':{}, 'ability_bonuses': {}}
        ##dicts present
        for grouping in ['abilities','ability_bonuses']:
            if grouping in lowerdex:
                if type(lowerdex[grouping]) is dict:
                    cleandex[grouping] = lowerdex[grouping]
                elif type(lowerdex[grouping]) is list and len(lowerdex[grouping]) == 6:
                    cleandex[grouping] = {ability_names[i]: lowerdex[grouping][i] for i in range(0,6)}
                else:
                    raise TypeError("Cannot parse "+grouping)
        # individual abilities overwrite
        #print("debug... ",cleandex['ability_bonuses'])
        for k in lowerdex:
            if k[0:3] in ability_names:
                cleandex['abilities'][k[0:3]] = int(lowerdex[k])
                if 'ab_'+k not in lowerdex:
                    cleandex['abilities'][k[0:3]] = math.floor(int(lowerdex[k])/2-5)
            elif k in ['ab_str', 'ab_dex', 'ab_con', 'ab_wis', 'ab_int', 'ab_cha']:
                cleandex['ability_bonuses'][k[3:6]] = int(lowerdex[k])
                if k[3:6] not in lowerdex:
                    cleandex['abilities'][k[3:6]] = int(lowerdex[k])*2+10
            elif k in ['abilities','ability_bonuses']:
                pass
            else:
                cleandex[k] = lowerdex[k]
        #print("debug... ",cleandex['ability_bonuses'])
        return cleandex

    def _set(self, item, alt=None, expected_type='string'):
        """
        Method to set the attribute named item based on that in self.settings if present, if not it uses alt value.
        :param item: the name of the self.settings key and attribute of self to set.
        :param alt: default value
        :param expected_type: "string" or "int" for now. Can be easily changed for other types.
        :return: None.
        """
        if item in self.settings:
            if expected_type == 'string':
                setattr(self, item, self.settings[item])
            elif expected_type == 'int':
                setattr(self, item, int(self.settings[item]))
        else:
            setattr(self, item, alt)

    def _initialise_abilities(self):
        """
        Rewritten so that cleaning module does the cleaning.
        :return: None.
        """
        self.able = 1  # has abilities. if nothing at all is provided it goes to zero. This is for rocks...
        # set blanks
        self.ability_bonuses = {n: 0 for n in self.ability_names} #default for no given ability score is 10 (bonus = 0) as per manual.
        self.abilities = {n: 10 for n in self.ability_names}
        for ability in self.settings['abilities']: #a dictionary within a dictionary
            if ability in self.settings['ability_bonuses']:
                if 10+self.settings['ability_bonuses'][ability]*2 != self.settings['abilities'][ability] and 10+self.settings['ability_bonuses'][ability]*2 +1 != self.settings['abilities'][ability]:
                    warnings.warn('Mismatch: both ability score and bonus provided, ' \
                    'but they differ ({0}: 10+{1}*2 vs. {2})'.format(ability,self.settings['ability_bonuses'][ability], self.settings['abilities'][ability]))
            self.abilities[ability] = int(self.settings['abilities'][ability])
            self.ability_bonuses[ability] = math.floor(int(self.settings['abilities'][ability])/2-5)
        for ability in self.settings['ability_bonuses']:
            self.ability_bonuses[ability] = self.settings['ability_bonuses'][ability]
            self.abilities[ability] = 10 + 2 * self.ability_bonuses[ability] #I know it means nothing, but I am unsure why this was absent.

    def _fill_from_dict(self, dictionary):
        return self._initialise(**dictionary)

    def _fill_from_beastiary(self, name):
        if name in self.beastiary:
            return self._initialise(**self.beastiary[name])
        else:
            ###For now fallback to preset. In future preset will be removed?
            return self._fill_from_preset(name)

    def _fill_from_preset(self, name):
        """
        Legacy... It might stop working due to code changes.
        :param name: the name of creature.
        :return: the stored creature.
        """
        if name == "netsharpshooter":
            self._initialise(name="netsharpshooter",
                             alignment="good",
                             hp=18, ac=18, hd = 8,
                             initiative_bonus=2,
                             healing_spells=6, healing_bonus=3, healing_dice=4, sc_ability="cha",
                             attack_parameters=[['rapier', 4, 2, 8]], alt_attack=['net', 4, 0, 0], level=3)
        elif name == "bard":
            self._initialise(name="Bard", alignment="good",
                             hp=18, ac=18,
                             healing_spells=6, healing_bonus=3, healing_dice=4,
                             initiative_bonus=2,
                             attack_parameters=[['rapier', 4, 2, 8]], level=3)

        elif name == "generic_tank":
            self._initialise(name="generic tank", alignment="good",
                             hp=20, ac=17,
                             initiative_bonus=2,
                             attack_parameters=[['great sword', 5, 3, 6, 6]], level=3)

        elif name == "mega_tank":
            self._initialise(name="mega tank", alignment="good",
                             hp=24, ac=17,
                             initiative_bonus=2,
                             attack_parameters=[['great sword', 5, 3, 10]], level=3)

        elif name == "a_b_dragon":
            self._initialise(name="Adult black dragon (minus frightful)", alignment="evil",
                             ac=19, hp=195, initiative_bonus=2,
                             attack_parameters=[['1', 11, 6, 10, 10], ['2', 11, 6, 6, 6], ['2', 11, 4, 6, 6]])

        elif name == "y_b_dragon":
            self._initialise(name="Young black dragon", alignment="evil",
                             ac=18, hp=127,
                             initiative_bonus=2,
                             attack_parameters=[['1', 7, 4, 10, 10, 8], ['2', 7, 4, 6, 6], ['2', 7, 4, 6, 6]])

        elif name == "frost_giant":
            self._initialise(name="Frost Giant", alignment="evil",
                             ac=15, hp=138,
                             attack_parameters=[['club', 9, 6, 12, 12, 12], ['club', 9, 6, 12, 12, 12]])

        elif name == "hill_giant":
            self._initialise(name="Hill Giant", alignment="evil",
                             ac=13, hp=105,
                             attack_parameters=[['club', 8, 5, 8, 8, 8], ['club', 8, 5, 8, 8, 8]])

        elif name == "goblin":
            self._initialise(name="Goblin", alignment="evil",
                             ac=15, hp=7,
                             initiative_bonus=2,
                             attack_parameters=[['sword', 4, 2, 6]])

        elif name == "hero":
            self._initialise(name="hero", alignment="good",
                             ac=16, hp=18,  # bog standard shielded leather-clad level 3.
                             attack_parameters=[['longsword', 4, 2, 8]])

        elif name == "antijoe":
            self._initialise(name="antiJoe", alignment="evil",
                             ac=17, hp=103,  # bog standard leather-clad level 3.
                             attack_parameters=[['shortsword', 2, 2, 6]])

        elif name == "joe":
            self._initialise(name="Joe", alignment="good",
                             ac=17, hp=103,  # bog standard leather-clad level 3.
                             attack_parameters=[['shortsword', 2, 2, 6]])

        elif name == "bob":
            self._initialise(name="Bob", alignment="mad",
                             ac=10, hp=8,
                             attack_parameters=[['club', 2, 0, 4], ['club', 2, 0, 4]])

        elif name == "allo":
            self._initialise(name="Allosaurus", alignment="evil",
                             ac=13, hp=51,
                             attack_parameters=[['claw', 6, 4, 8], ['bite', 6, 4, 10, 10]])

        elif name == "anky":
            self._initialise("Ankylosaurus",
                             ac=15, hp=68, alignment='evil',
                             attack_parameters=[['tail', 7, 4, 6, 6, 6, 6]],
                             log="CR 3 700 XP")

        elif name == "my barbarian":
            self._initialise(name="Barbarian",
                             ac=18, hp=66, alignment="good",
                             attack_parameters=[['greatsword', 4, 1, 6, 6], ['frenzy greatsword', 4, 1, 6, 6]],
                             log="hp is doubled due to resistance", level=3)

        elif name == "my druid":
            self._initialise(name="Twice Brown Bear Druid",
                             hp=86, ac=11, alignment="good",
                             attack_parameters=[['claw', 5, 4, 8], ['bite', 5, 4, 6, 6]],
                             ability_bonuses=[0, 0, 0, 0, 3, 0],
                             sc_ability='wis', buff='cast_barkskin', buff_spells=4,
                             log='The hp is bear x 2 + druid', level=3)

        elif name == "inert":
            self._initialise(name="inert", alignment="bad",
                             ac=10, hp=20,
                             attack_parameters=[['toothpick', 0, 0, 2]])

        elif name == "test":
            self._initialise(name="Test", alignment="good",
                             ac=10, hp=100,
                             attack_parameters=[['club', 2, 0, 4]])

        elif name == "polar":
            self._initialise(name="polar bear", alignment='evil',
                             ac=12, hp=42,
                             attack_parameters=[['bite', 7, 5, 8], ['claw', 7, 5, 6, 6]])

        elif name == "paradox":
            self._initialise(name="Paradox", alignment="evil",
                             ac=10, hp=200,
                             attack_parameters=[['A', 2, 0, 1]])

        elif name == "commoner":
            self._initialise(name="Commoner", alignment="good",
                             ac=10, hp=4,
                             attack_parameters=[['club', 2, 0, 4]])

        elif name == "giant_rat":
            self._initialise(name="Giant Rat", alignment="evil",
                             hp=7, ac=12,
                             initiative_bonus=2,
                             attack_parameters=[['bite', 4, 2, 4]])

        elif name == "twibear":
            self._initialise(name="Twice Brown Bear Druid",
                             hp=86, ac=11, alignment="good",
                             attack_parameters=[['claw', 5, 4, 8], ['bite', 5, 4, 6]], level=3)

        elif name == "barkskin_twibear":
            self._initialise(name="Druid twice as Barkskinned Brown Bear",
                             hp=86, ac=16, alignment="good",
                             attack_parameters=[['claw', 5, 4, 8], ['bite', 5, 4, 6]], level=3)

        elif name == "barkskin_bear":
            self._initialise(name="Barkskinned Brown Bear", alignment="good",
                             hp=34, ac=16,
                             attack_parameters=[['claw', 5, 4, 8], ['bite', 5, 4, 6]], level=4, hd=10)

        elif name == "giant_toad":
            self._initialise(name="Giant Toad", alignment="evil",
                             hp=39, ac=11,
                             attack_parameters=[['lick', 4, 2, 10, 10]])

        elif name == "cthulhu":  # PF stats. who cares. you'll die.
            self._initialise(name="Cthulhu", alignment="beyond",
                             ac=49, hp=774, xp=9830400,
                             initiative_bonus=15,
                             attack_parameters=[['2 claws', 42, 23, 6, 6, 6, 6], ['4 tentacles', 42, 34, 10, 10]],
                             alt_attack=['none', 0],
                             healing_spells=99999, healing_dice=1, healing_bonus=30,
                             ability_bonuses=[56, 21, 45, 31, 36, 34], sc_ability='wis',
                             buff='cast_nothing', buff_spells=0, log=None, hd=8, level=36, proficiency=27)

        else:
            self._initialise(name="Commoner", alignment="evil",
                             ac=10, hp=4,
                             attack_parameters=[['club', 2, 0, 4]])

    def set_level(self, level=None):
        """
        Alter the level of the creature.
        :param level: opt. int, the level. if absent it will set it to the stored level.
        :return: nothing. changes self.
        """
        if not level:
            level = self.level
        old_level = self.level
        if not self.hd:
                warnings.warn('No hit dice specified, setting to d8')
        if not old_level: #zero???
            self.hp = 0
            self.hd.crit = 1  # Not-RAW first level is always max for PCs, but not monsters.
            for x in range(level):
                self.hp += self.hd.roll()
        else:
            for x in range(level-old_level):
                self.hp += self.hd.roll()
        self.level = level
        self.starting_hp = self.hp
        self.proficiency = 1 + round((level) / 4)
        if hasattr(self, 'attacks'):
            for attack in self.attacks:
                attack['attack'].bonus += self.proficiency - 1 + round((old_level) / 4)
                #Changing by delta proficiency as there is no way of knowing what weapon bonuses there may be etc.

    def change_attribute(self,**abilities):
        """
        Setting an ability attribute directly does not result in a recalculation.
        For example:
        >>> slashr = Creature('troll')
        >>> slashr.abilities['cha'] = 16
        This will not change the stats dependent on that ability.
        This method attempts to change the dependent abilities.
        A late addition, so the code does not make use of it.
        :param attributes: key value pair
        :return: None
        """
        for attr in abilities:
            attr = attr[0:3].lower() #just in case
            if attr in self.abilities:
                old_attr=self.abilities[attr]
                self.abilities[attr]=int(abilities[attr])
                delta=math.floor(self.abilities[attr]/2-5)-math.floor(old_attr/2-5)
                old_bonus=self.ability_bonuses[attr]
                self.ability_bonuses[attr] +=delta #it might differ for some reason...
                #con does not change
                if attr == "str":
                    pass
                elif attr == "dex":
                    pass
                elif attr == "con":
                    pass
                elif attr == "int":
                    pass
                elif attr == "wis":
                    pass
                elif attr == "cha":
                    pass



            else:
                raise ValueError('Unrecognised ability')

    def copy(self):
        """
        :return: a copy of the creature. with an altered name.
        """
        self.copy_index += 1
        return Creature(self, name=self.name + ' ' + str(self.copy_index))

    def _attack_parse(self, attack_parameters):
        """
        `self.attacks` has a list of attacks. Each attack is a dictionary of `name` string, `attack` Dice and `damage` Dice.
        Dice holds the dice(s) and the bonuses and other properties.
        :param attack_parameters: A not-parsed set of attacks: a list of a list of attack bonus int, damage bonus int and damage dice size int/list
        :return: None (changes self.attacks)
        """
        #if type(attack_parameters) is str:
        #    import json
        #    attack_parameters = json.loads(attack_parameters)
        self.attacks = []
        for monoattack in attack_parameters:
            att = {'name': monoattack[0]}
            att['damage'] = Dice(monoattack[2], monoattack[3:], role="damage")
            att['attack'] = Dice(monoattack[1], 20, role="attack", twinned=att['damage'])
            self.attacks.append(att)
        for x in self.attacks:
            self.hurtful += x['damage'].bonus
            self.hurtful += (sum(x['damage'].dice) + len(
                x['damage'].dice)) / 2  # the average roll of a d6 is not 3 but 3.5

    def __str__(self):
        if self.tally['battles']:
            battles = self.tally['battles']
            return self.name + ": {team=" + self.alignment + "; avg hp=" + str(
                self.tally['hp'] / battles) + " (from " + str(
                self.starting_hp) + "); avg healing spells left=" + str(
                self.tally['healing_spells'] / battles) + " (from " + str(
                self.starting_healing_spells) + "); damage done (per battle average)= " + str(
                self.tally['damage'] / battles) + "; hits/misses (PBA)= " + str(
                self.tally['hits'] / battles) + "/" + str(
                self.tally['misses'] / battles) + "; rounds (PBA)=" + str(
                self.tally['rounds'] / battles) + ";}"
        else:
            return self.name + ": UNTESTED IN BATTLE"

    def isalive(self):
        if self.hp > 0: return 1

    def take_damage(self, points, verbose=0):
        self.hp -= points
        if verbose: verbose.append(self.name + ' took ' + str(points) + ' of damage. Now on ' + str(self.hp) + ' hp.')
        if self.concentrating:
            dc = points / 2
            if dc < 10: dc = 10
            if Dice(self.ability_bonuses[self.sc_ab]).roll() < dc:
                self.conc_fx()
                if verbose: verbose.append(self.name + ' has lost their concentration')

    def ready(self):
        self.dodge = 0
        # there should be a few more.
        # conditions.

    def reset(self, hard = False):
        """
        Resets the creature back to health (a long rest). a hard reset resets its scores
        :param hard: bool, false keeps tallies
        :return: None
        """
        self.hp = self.starting_hp
        if self.concentrating:
            self.conc_fx() #TODO this looks fishy
        self.healing_spells = self.starting_healing_spells
        if hard:
            self.tally={'damage': 0,'hp': 0, 'hits': 0,'misses': 0,'rounds': 0,'healing_spells': 0,'battles': 0,'dead':0}


    def check_advantage(self, opponent):
        adv = 0
        if opponent.dodge:
            adv += -1
        if (opponent.condition == 'netted') or (opponent.condition == 'restrained'):
            adv += 1
        # Per coding it is impossible that a netted creature attempts an attack.
        if (self.condition == 'netted') or (self.condition == 'restrained'):
            adv += -1
        return adv

    def net(self, opponent, verbose=0):
        self.alt_attack['attack'].advantage = self.check_advantage(opponent)
        if self.alt_attack['attack'].roll(verbose) >= opponent.ac:
            opponent.condition = 'netted'
            self.tally['hits'] += 1
            if verbose: verbose.append(self.name + " netted " + opponent.name)
        else:
            self.tally['misses'] += 1

    def cast_barkskin(self):
        if self.concentrating == 0:
            self.temp = self.ac
            self.ac = 16
            self.concentrating = 1
        elif self.concentrating == 1:
            self.ac = self.temp
            self.concentrating = 0

    def cast_nothing(self, state='activate'):  # Something isn't quite right if this is invoked.
        pass

    def heal(self, points, verbose=0):
        self.hp += points
        if verbose: verbose.append(self.name + ' was healed by ' + str(points) + '. Now on ' + str(self.hp) + ' hp.')

    def assess_wounded(self, verbose=0):
        targets = self.arena.find('bloodiest allies')
        if len(targets) > 0:
            weakling = targets[0]
            if weakling.starting_hp > (self.healing.dice[0] + self.healing.bonus + weakling.hp):
                if verbose: verbose.append(self.name + " wants to heal " + weakling.name)
                return weakling
            else:
                return 0
        else:
            raise NameError('A dead man wants to heal folk')

    def cast_healing(self, weakling, verbose=0):
        if self.healing_spells > 0:
            weakling.heal(self.healing.roll(), verbose)
            self.healing_spells -= 1

    def multiattack(self, verbose=0, assess=0):
        if assess:
            return 0  # the default
        for i in range(len(self.attacks)):
            try:
                opponent = self.arena.find(TARGET, self)[0]
            except IndexError:
                raise self.arena.Victory()
            if verbose:
                verbose.append(self.name + ' attacks ' + opponent.name + ' with ' + str(self.attacks[i]['name']))
            # This was the hit method. put here for now.
            self.attacks[i]['attack'].advantage = self.check_advantage(opponent)
            if self.attacks[i]['attack'].roll(verbose) >= opponent.ac:
                # self.attacks[i]['damage'].crit = self.attacks[i]['attack'].crit  #Pass the crit if present.
                h = self.attacks[i]['damage'].roll(verbose)
                opponent.take_damage(h, verbose)
                self.tally['damage'] += h
                self.tally['hits'] += 1
            else:
                self.tally['misses'] += 1

    # TODO
    def check_action(self, action, verbose):
        return getattr(self, action)(assess=1)

    # TODO
    def do_action(self, action, verbose):
        # do it.
        pass

    # TODO
    def TBA_act(self, verbose=0):
        if not self.arena.find('alive enemy'):
            raise Encounter.Victory()
        x = {'nothing': 'cast_nothing'}
        choice = [self.check_action(x) for x in self.actions]
        best = sorted(choice.keys(), key=choice.get)[0]
        self.do_action(best)

    def act(self, verbose=0):
        if not self.arena.find('alive enemy'):
            raise Encounter.Victory()
        # BONUS ACTION
        # heal  -healing word, a bonus action.
        if self.healing_spells > 0:
            weakling = self.assess_wounded(verbose)
            if weakling != 0:
                self.cast_healing(weakling, verbose)
        # Main action!
        economy = len(self.arena.find('allies')) > len(self.arena.find('opponents')) > 0
        # Buff?
        if self.condition == 'netted':
            # NOT-RAW: DC10 strength check or something equally easy for monsters
            if verbose: verbose.append(self.name + " freed himself from a net")
            self.condition = 'normal'
        elif self.buff_spells > 0 and self.concentrating == 0:
            self.conc_fx()
            if verbose: verbose.append(self.name + ' buffs up!')
            # greater action economy: waste opponent's turn.
        elif economy and self is self.arena.find('weakest allies')[0]:
            if verbose: verbose.append(self.name + " is dodging")
            self.dodge = 1
        elif economy and self.alt_attack['name'] == 'net':
            opponent = self.arena.find('fiersomest enemy alive', self)[0]
            if opponent.condition != 'netted':
                self.net(opponent, verbose)
            else:
                self.multiattack(verbose)
        else:
            self.multiattack(verbose)

    def generate_character_sheet(self):
        """
        An markdown character sheet.
        :return: a string
        """
        def writeline(field,value,secvalue=None):
            #returns _field_: value (secvalue)
            #secvalues is if has a secondary value to be added in brachets
            if not secvalue:
                return '_'+str(field).replace("_"," ")+'_: '+str(value)+'  \n'
            else:
                return '_'+str(field).replace("_"," ")+'_: '+str(value)+' ('+str(secvalue)+')  \n'
        sheet = '# '+self.name.upper()+'\n'
        sheet +=  writeline('Name',self.name)
        sheet +=  writeline('Alignment',self.alignment)
        if self.cr:
            level = self.cr
            lname = 'CR'
        else:
            level = self.level
            lname = 'Level'
        if self.hd:
            sheet +=  writeline(lname+' (hit dice)',level,self.hd)
        else:
            sheet +=  writeline(lname,level)
        if self.xp:
            sheet += writeline('XP',self.xp)
        sheet += '## Abilities\n'
        for ab in self.ability_names:
            sheet +=  writeline(ab,self.abilities[ab],self.ability_bonuses[ab])
        sheet += '## Combat\n'
        sheet +=  writeline('Hit points (hp total)',self.hp,self.starting_hp)
        sheet +=  writeline('Condition',self.condition)
        sheet +=  writeline('Initiative',self.initiative)
        sheet +=  writeline('Proficiency',self.proficiency)
        sheet +=  writeline('Armour class',self.ac)
        sheet += '### Attacks\n'
        sheet +=  writeline('Potential average damage per turn',self.hurtful)
        for d in self.attacks:
                sheet += "* "+ writeline(d['name'],d['attack'],d['damage'])
        sheet += '### Raw data\n'
        sheet+=str(self.__dict__).replace('<br/>','\n')
        return sheet



######################ARENA######################
class Encounter:
    """
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
    """

    class Victory(Exception):
        """
        The way the encounter ends is a victory error is raised to stop the creatures from acting further.
        """
        pass

    def __init__(self, *lineup):
        # print(lineup)
        # self.lineup={x.name:x for x in lineup}
        # self.lineup = list(lineup)  #Classic fuck-up
        self.tally = {'rounds': 0, 'battles': 0, 'perfect': None, 'close': None, 'victories': None}
        self.active = None
        self.name = 'Encounter'
        self.masterlog = []
        self.note = ''
        self.combattants = []
        for chap in lineup:
            self.append(chap)
        self.blank()

    def blank(self, hard=True):
        # this resets the teams
        self.sides = set([dude.alignment for dude in self])
        self.tally['battles'] = 0
        self.tally['rounds'] = 0
        self.tally['perfect'] = {side: 0 for side in self.sides}
        self.tally['close'] = {side: 0 for side in self.sides}
        self.tally['victories'] = {side: 0 for side in self.sides}
        self.reset(hard)


    def append(self, newbie):
        if not type(newbie) is Creature:
            newbie = Creature(newbie)  # Is this safe??
        self.combattants.append(newbie)
        newbie.arena = self
        self.blank()

    def extend(self, iterable):
        for x in iterable:
            self.append(x)
        return self

    def addmob(self, n):
        """
        Adds _n_ commoners to the battle
        :param n: number of commoners
        :return: self
        """
        for x in range(int(n)):
            self.append("commoner")
        return self

    def __str__(self):
        string = "=" * 50 + ' ' + self.name + " " + "=" * 50 + N
        string += self.predict()
        string += "-" * 110 + N
        string += "Battles: " + str(self.tally['battles']) + "; Sum of rounds: " + str(
            self.tally['rounds']) + "; " + self.note + N
        for s in self.sides:
            string += "> Team " + str(s) + " = winning battles: " + str(
                self.tally['victories'][s]) + "; perfect battles: " + str(
                self.tally['perfect'][s]) + "; close-call battles: " + str(self.tally['close'][s]) + ";\n"
        string += "-" * 49 + " Combattants  " + "-" * 48 + N
        for fighter in self.combattants: string += str(fighter) + N
        return string

    def json(self):
        import json
        jsdic = {"prediction": self.predict(),
                 "battles": self.tally['battles'],
                 "rounds": self.tally['rounds'],
                 "notes": self.note,
                 "team_names": list(self.sides),
                 "team_victories": [self.tally['victories'][x] for x in list(self.sides)],
                 "team_perfects": [self.tally['perfect'][x] for x in list(self.sides)],
                 "team_close": [self.tally['close'][x] for x in list(self.sides)],
                 "combattant_names": [x.name for x in self.combattants],
                 "combattant_alignments": [x.alignment for x in self.combattants],
                 "combattant_damage_avg": [x.tally['damage'] / self.tally['battles'] for x in self.combattants],
                 "combattant_hit_avg": [x.tally['hits'] / self.tally['battles'] for x in self.combattants],
                 "combattant_miss_avg": [x.tally['misses'] / self.tally['battles'] for x in self.combattants],
                 "combattant_rounds": [x.tally['rounds'] / self.tally['rounds'] for x in self.combattants],
                 "sample_encounter": N.join(self.masterlog)
                 }
        return json.dumps(jsdic)

    def __len__(self):
        return len(self.combattants)

    def __add__(self, other):
        if type(other) is str:
            self.append(Creature(other))
        elif type(other) is Creature:
            self.append(other)
        elif type(other) is Encounter:
            self.extend(other.combattants)
        else:
            raise TypeError('Unsupported type '+str(type(other)))

    def __iter__(self):
        return iter(self.combattants)

    def __getitem__(self, item):
        for character in self:
            if character.name == item:
                return character
        raise Exception('Nobody by this name')

    def reset(self, hard=False):
        for schmuck in self.combattants:
            schmuck.reset(hard)
        return self

    def remove(self,moriturus):
        """
        Removes a creature and resets and rechecks
        :param moriturus: The creature name to be dropped
        :return: self
        """
        if type(moriturus) is str:
            for chap in self.combattants:
                if chap.name == moriturus:
                    self.combattants.remove(chap)
                    break
            else:
                raise ValueError(moriturus+' not found in Encounter among '+"; ".join([chap.name for chap in self.combattants]))
        elif type(moriturus) is Creature:
            self.combattants.remove(moriturus)
        self.blank()



    def set_deathmatch(self):
        colours = 'red blue green orange yellow lime cyan violet ultraviolet pink brown black white octarine teal magenta blue-green fuchsia purple cream grey'.split(
            ' ')
        for schmuck in self:
            schmuck.alignment = colours.pop(0) + " team"
        return self

    def roll_for_initiative(self, verbose=0):
        self.combattants = sorted(self.combattants, key=lambda fighter: fighter.initiative.roll())
        if verbose:
            verbose.append("Turn order:")
            verbose.append(str([x.name for x in self]))

    def predict(self):
        def safediv(a, b, default=0):
            try:
                return a / b
            except:
                return default

        def not_us(side):
            (a, b) = list(self.sides)
            if a == side:
                return b
            else:
                return a

        if len(self.sides) != 2:
            # print('Calculations unavailable for more than 2 teams')
            return "Prediction unavailable for more than 2 teams"
        t_ac = {x: [] for x in self.sides}
        for character in self:
            t_ac[character.alignment].append(character.ac)
        ac = {x: sum(t_ac[x]) / len(t_ac[x]) for x in t_ac.keys()}
        damage = {x: 0 for x in self.sides}
        hp = {x: 0 for x in self.sides}
        for character in self:
            for move in character.attacks:
                move['damage'].avg = True
                damage[character.alignment] += safediv((20 + move['attack'].bonus - ac[not_us(character.alignment)]),
                                                       20 * move['damage'].roll())
                move['damage'].avg = False
                hp[character.alignment] += character.starting_hp
        (a, b) = list(self.sides)
        rate = {a: safediv(hp[a], damage[b], 0.0), b: safediv(hp[b], damage[a], 0.0)}
        return ('Rough a priori predictions:' + N +
                '> ' + str(a) + '= expected rounds to survive: ' + str(
            round(rate[a], 2)) + '; crudely normalised: ' + str(
            round(safediv(rate[a], (rate[a] + rate[b]) * 100))) + '%' + N +
                '> ' + str(b) + '= expected rounds to survive: ' + str(
            round(rate[b], 2)) + '; crudely normalised: ' + str(
            round(safediv(rate[b], (rate[a] + rate[b]) * 100))) + '%' + N)

    def battle(self, reset=1, verbose=1):
        if verbose: self.masterlog.append('==NEW BATTLE==')
        self.tally['battles'] += 1
        if reset: self.reset()
        for schmuck in self: schmuck.tally['battles'] += 1
        self.roll_for_initiative(self.masterlog)
        while True:
            try:
                if verbose: self.masterlog.append('**NEW ROUND**')
                self.tally['rounds'] += 1
                for character in self:
                    character.ready()
                    if character.isalive():
                        self.active = character
                        character.tally['rounds'] += 1
                        character.act(self.masterlog)
                    else:
                        character.tally['dead'] += 1
            except Encounter.Victory:
                break
        # closing up maths
        side = self.active.alignment
        team = self.find('allies')
        self.tally['victories'][side] += 1
        perfect = 1
        close = 0
        for x in team:
            if x.hp < x.starting_hp:
                perfect = 0
            if x.hp < 0:
                close = 1
        if not perfect:
            self.tally['perfect'][side] += perfect
        self.tally['close'][side] += close
        for character in self:
            character.tally['hp'] += character.hp
            character.tally['healing_spells'] += character.healing_spells
        if verbose: self.masterlog.append(str(self))
        # return self or side?
        return self

    def go_to_war(self, rounds=1000):
        for i in range(rounds):
            self.battle(1, 0)
        x = {y: self.tally['victories'][y] for y in self.sides}
        se = {}
        for i in list(x):
            x[i] /= rounds
            try:
                se[i] = math.sqrt(x[i] * (1 - x[i]) / rounds)
            except Exception:
                se[i] = "NA"
        self.reset()
        for i in list(x):
            try:
                self.note += str(i) + ': ' + str(round(float(x[i]), 2)) + ' ± ' + str(round(float(se[i]), 2)) + '; '
            except:
                self.note += str(i) + ': ' + str(x[i]) + ' ± ' + str(se[i]) + '; '
        return self

    def find(self, what, searcher=None, team=None):

        def _enemies(folk):
            return [query for query in folk if (query.alignment != team)]

        def _allies(folk):
            return [query for query in folk if (query.alignment == team)]

        def _alive(folk):
            return [query for query in folk if (query.hp > 0)]

        def _normal(folk):
            return [joe for joe in folk if joe.condition == 'normal']

        def _random(folk):
            random.shuffle(folk)
            return folk

        def _weakest(folk):
            return sorted(folk, key=lambda query: query.hp)

        def _bloodiest(folk):
            return sorted(folk, key=lambda query: query.hp - query.starting_hp)

        def _fiersomest(folk):
            return sorted(folk, key=lambda query: query.hurtful, reverse=True)

        def _opponents(folk):
            return _alive(_enemies(folk))

        searcher = searcher or self.active
        team = team or searcher.alignment
        folk = self.combattants
        agenda = list(what.split())
        opt = {
            'enemies': _enemies,
            'enemy': _enemies,
            'opponents': _opponents,
            'allies': _allies,
            'ally': _allies,
            'normal': _normal,
            'alive': _alive,
            'fiersomest': _fiersomest,
            'weakest': _weakest,
            'random': _random,
            'bloodiest': _bloodiest
        }
        for cmd in list(agenda):  # copy it.
            if folk == None:
                folk = []
            for o in opt:
                if (cmd == o):
                    folk = opt[o](folk)
                    agenda.remove(cmd)
        if agenda:
            raise Exception(str(cmd) + ' field not found')
        return folk


########### Junk methods #####

def tarrasquicide():
    print('Test module...of sorts: 128 commoners can kill a tarrasque')
    print('how many commoners are needed to kill a tarasque')
    ted = Creature("tarrasque")
    print(ted)
    wwe = Encounter(ted, "commoner", "commoner").battle(1, 1)

    print(wwe.masterlog)
    max = 1
    while not wwe.tally['victories']['good']:
        max *= 2
        x = ["commoner" for x in range(int(max))]
        wwe.extend(x).battle(1, 0)
        wwe.tally['victories']['good']
        print(str(int(max)) + " commoners: " + str(wwe.tally['victories']['good']))
        print(ted.hp)

def creature_check(who= 'commoner'):
    """
    Dev test area. Prints the abilities of a given creature from the beastiary to see if all is okay.
    :param who: name
    :return: None
    """
    print('Ability bonus...')
    print('Beastiary: ',{x: Creature.beastiary[who][x] for x in 'AB_Str AB_Int AB_Con AB_Cha AB_Dex AB_Wis'.split()})
    print('Instance: ',Creature(who).ability_bonuses)
    print('Mod: ',Creature(who,str=999).ability_bonuses)


if __name__ == "__main__":
    pass
    #TODO I was updating the change_ability method of creature
