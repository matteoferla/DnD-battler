# inherited by CreatureFiller along with CreatureLoader

from DnD_battler.creature._init_abilities import CreatueInitAble
from DnD_battler.creature._safe_property import CreatureSafeProp
from DnD_battler.dice import Dice

import json


class CreatureInitialise(CreatueInitAble, CreatureSafeProp):

    def _initialise(self, **settings):
        """
        Preface.
        Character creation in DnD_battler is rather painful. Here due to missing it is even more complex.
        Also, creature, character and monster are used interchangably here unfortunately, which will be fixed one day.
        The method _set

        This is the order of creation. All attributes are in lowercase regardless of the style on the PHB.

        1. a creature can be based off another, if the `base attribute is set`(str or Creature).
        2. set `name`
        3. set `level` (def 1)
        4. set `xp` (def None)
        5. set `proficiency` (proficiency bonus), 1 + round(self.level / 4) if absent,
            but will be overidden if hp is not specified as the `set_level` will generate it from HD and level
        6. set ability bonues (`set_ability_dice` method). To let the user give a base creature
            and weak a single ability (__e.g.__ `Creature('Commoner',name='mutant commoner', str=20)),
            the creature has abilities as individual attributes with three letter codes, __e.g.__ `self.str`
            and as a dictionary (`self.abilities`),
            while `self.ability_bonuses` has a twin that is the suffix `_bonus` (__e.g.__ `self.str_bonus`).
        7. set `hp`
        8. AC (`self.armor`)
        9. spellcasting (complex, may change in future): `sc_ab` the spellcasting ability as three char str,
        10. `initiative_bonus`
        11. combat stats... attack_parameters=[['rapier', 4, 2, 8]], alt_attack=['net', 4, 0, 0]

        name,
        alignment="good",
        ac=10,
        initiative_bonus=None,
        hp=None,
        attack_parameters=[['club', 2, 0, 4]], alt_attack=['none', 0],
        healing_spells=0, healing_dice=4, healing_bonus=None,
        ability_bonuses=[0, 0, 0, 0, 0, 0], sc_ability='wis',
        buff='cast_nothing', buff_spells=0,
        log=None,
        xp=0, hd=6,
        level=1,
        proficiency=2
        """
        if settings:
            self.settings = self.clean_settings(settings)
        else:
            # same as self._fill_from_preset('commoner')
            self._initialise(name="Commoner", alignment="neutral",
                             ac=10, hp=4,
                             attack_parameters=[['club', 2, 0, 4]])
            print("EMPTY CREATURE GIVEN. SETTING TO COMMONER")
            return 0

        # Mod of preexisting
        if 'base' in self.settings:
            # Sanify first and make victim
            if type(self.settings['base']) is str:
                # generate a preset and get its attributes. Seems a bit wasteful.
                victim = self.__class__(self.settings['base'])
            elif isinstance(self.settings['base'], self.__class__):
                victim = self.settings['base']
            else:
                raise TypeError
            # copy all
            # victim.ability_bonuses #in case the user provided with ability scores,
            # which are overridden by adbility bonues
            base = {x: getattr(victim, x) for x in dir(victim) if
                    getattr(victim, x) and x.find("__") == -1 and x.find("_") != 0 and x != 'beastiary'}
            base['ability_bonuses'] = {}
            # base.update(**self.settings)
            for (k, v) in self.settings.items():
                if type(v) is dict:
                    base[k].update(v)
                else:
                    base[k] = v
            self.settings = base

        # Name etc.
        # subscript assigns it or self.settings if it has a value
        self['name'] = 'nameless'
        self['level'] = 0
        self['xp'] = 0
        # proficiency. Will be overridden if hp is provided?
        self['proficiency'] = 1 + round(self.level / 4)  # TODO check maths on PH

        # set abilities
        self.set_ability_dice()

        # Get HD
        self.hit_die = None
        if 'hd' in self.settings.keys():
            if type(self.settings['hd']) is Dice:
                self.hit_die = self.settings['hd']  # we're dealing with a copy of a beastiary obj.
            else:
                self.hit_die = Dice(num_faces=int(self.settings['hd']),
                               bonus=self.con.bonus,
                               avg=True,
                               role="hd")
        elif 'size' in self.settings.keys():
            size_cat = {"small": 6, "medium": 8, "large": 10, "huge": 12}
            if self.settings['size'] in size_cat.keys():
                self.hit_die = Dice(bonus=self.con.bonus,
                               num_faces=size_cat[self.settings['size']],
                               avg=True,
                               role="hd")
        elif 'hp' in self.settings and 'level' in self.settings:
            # Guess based on hp and level. It is not that dodgy really as the manual does not use odd dice.
            # hp =approx. 0.5 HD * (level-1) + HD + con * level
            # HD * (0.5* (level-1)+1) = hp - con*level
            # HD = (hp - con*level)/(level+1)
            bestchoice = (int(self.settings['hp']) - self.con.bonus * int(self.settings['level'])) / (
                (int(self.settings['level']) + 1))
            print(int(self.settings['hp']), int(self.ability_bonuses['con']), int(self.settings['level']))
            print("choice HD...", bestchoice)
            # print("diagnosis...",self.ability_bonuses)
            self.log.warning('Unfinished case to guess HD. so Defaulting hit dice to d8 instead')  # TODO finish
            self.hit_die = Dice(bonus=self.con.bonus, num_faces=8, avg=True, role="hd")
        else:
            # defaulting to d8
            self.log.warning('Insufficient info: defaulting hit dice to d8')
            self.hit_die = Dice(bonus=self.con.bonus, num_faces=8, avg=True, role="hd")

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
            self.settings['ac'] = 10 + self.dex.bonus
        self.ac = int(self.settings['ac'])

        # init
        if not 'initiative_bonus' in self.settings:
            self.settings['initiative_bonus'] = self.dex.bonus
        self.initiative = Dice(bonus=int(self.settings['initiative_bonus']),
                               num_faces=20,
                               role="initiative")

        ##spell casting ability_bonuses
        if 'sc_ability' in self.settings:
            self.spellcasting_ability_name = self.settings['sc_ability'].lower()
        elif 'healing_spells' in self.settings or 'buff_spells' in self.settings:
            self.spellcasting_ability_name = max('wis', 'int', 'cha',
                             key=lambda ab: self[ab].bonus)  # Going for highest. seriously?!
            print(
                "Please specify spellcasting ability of " +
                self.name +
                " next time, this time " +
                self.spellcasting_ability_name +
                " was used as it was biggest.")
        else:
            self.spellcasting_ability_name = 'con'  # TODO fix this botch up.
        if not 'healing_bonus' in self.settings:
            self.settings['healing_bonus'] = self[self.spellcasting_ability_name].bonus
        if 'healing_spells' in self.settings:
            self.starting_healing_spells = int(self.settings['healing_spells'])
            self.healing_spells = self.starting_healing_spells
            if not 'healing_dice' in self.settings:
                self.settings['healing_dice'] = 4  # healing word.
            self.healing = Dice(bonus=int(self.settings['healing_bonus']),
                                num_faces=int(self.settings['healing_dice']),
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
                x = json.loads(self.settings['attack_parameters'].replace("*", "\""))
                self._attack_parse(x)
                self.attack_parameters = x
            except:
                # These have to be readable by _attack_parse
                weapons = {'club': 4, 'greatclub': 8,
                           'dagger': 4, 'shortsword': 6, 'longsword': 8, 'bastardsword': 10, 'greatsword': 12,
                           'rapier': 8, 'scimitar': 6, 'sickle': 4,
                           'handaxe': 6, 'battleaxe': 8, 'waraxe': 10, 'greataxe': 12,
                           'javelin': 6, 'spear': 6, 'flail': 8, 'glaive': 10, 'halberd': 10, 'lance': 12, 'pike': 10,
                           'trident': 6,
                           'war pick': 8,
                           'lighthammer': 4, 'mace': 6, 'warhammer': 8,
                           'quaterstaff': 6, 'morningstar': 8, 'punch': 1,
                           'whip': 4}  # parsing of strings for dice not implemented yet, so punch is d1 for now.
                # TODO weapons removed as they gave trouble:
                # 'maul':[6,6],
                # 'brütal war pick': [8, 8],  # okay, I could not resist it.

                # bastard sword and war axe are no more due to the versatile rule, however they were kept here to keep it simple
                # ranged weapons are missing for now...
                for w in weapons.keys():
                    if self.settings['attack_parameters'].lower().find(w) > -1:
                        # TODO fix the fact that a it gives the finesse option to all.
                        if self.dex.bonus > self.str.bonus:
                            chosen_ab = 'dex'
                        else:
                            chosen_ab = 'str'
                        self.attack_parameters = [[w, self.proficiency + chosen_ab, chosen_ab, weapons[w]]]
                        self._attack_parse(self.attack_parameters)
                        self.log += "Weapon matched by str to {w}\n"
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
                               'attack': Dice(bonus=self.settings['alt_attack'][1],
                                              num_faces=20)}  # CURRENTLY ONLY NETTING IS OPTION!
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
        self['custom'] = []
        for other in self.custom:
            if other == "conc_fx":
                getattr(self, self.settings['conc_fx'])
            else:
                self[other] = self.settings[other]  # force it to be set.

        self.arena = None
        self.settings = {}

    def clean_settings(self, dirtydex: dict) -> dict:
        """
        Sanify the settings

        :return: a cleaned dictionary
        """
        # lowercase
        lowerdex = {k.lower(): dirtydex[k] for k in dirtydex}

        # sort issue with abilities
        # TODO no longer valid
        cleandex = {'abilities': {}, 'ability_bonuses': {}}
        ##dicts present
        for grouping in ['abilities', 'ability_bonuses']:
            if grouping in lowerdex:
                if type(lowerdex[grouping]) is dict:
                    cleandex[grouping] = lowerdex[grouping]
                elif type(lowerdex[grouping]) is list and len(lowerdex[grouping]) == 6:
                    cleandex[grouping] = {self.ability_names[i]: lowerdex[grouping][i] for i in range(0, 6)}
                else:
                    raise TypeError("Cannot parse " + grouping)
        # individual abilities overwrite
        # print("debug... ",cleandex['ability_bonuses'])
        for k in lowerdex:
            if k[0:3] in self.ability_names:
                cleandex['abilities'][k[0:3]] = int(lowerdex[k])
                if 'ab_' + k not in lowerdex:
                    cleandex['abilities'][k[0:3]] = int(int(lowerdex[k]) / 2 - 5)
            elif k in ['ab_str', 'ab_dex', 'ab_con', 'ab_wis', 'ab_int', 'ab_cha']:
                cleandex['ability_bonuses'][k[3:6]] = int(lowerdex[k])
                if k[3:6] not in lowerdex:
                    cleandex['abilities'][k[3:6]] = int(lowerdex[k]) * 2 + 10
            elif k in ['abilities', 'ability_bonuses']:
                pass
            else:
                cleandex[k] = lowerdex[k]
        # print("debug... ",cleandex['ability_bonuses'])
        return cleandex





        # {x: getattr(victim, x) for x in dir(self) if
        #  getattr(victim, x) and x.find("__") == -1 and x.find("_") != 0 and x != 'beastiary'}
        # base['ability_bonuses'] = {}
        # # base.update(**self.settings)
        # for (k, v) in self.settings.items():
        #     if type(v) is dict:
        #         base[k].update(v)
        #     else:
        #         base[k] = v
