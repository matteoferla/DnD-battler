from ..dice import Ability

class CreatureBase:
    # inherited by utils

    ability_names = ['str', 'dex', 'con', 'wis', 'int', 'cha']

    def __init__(self): # this is to make PyCharm happy.
        self.arena = None
        self.settings = {}
        self.name = 'nameless'
        self.level = 0
        self.xp = 0
        self.proficiency = 0
        self.hd = None
        #Ability
        self.able = 1  # has abilities. if nothing at all is provided it goes to zero. This is for rocks...
        self.str = Ability(0)
        self.dex = Ability(0)
        self.con = Ability(0)
        self.wis = Ability(0)
        self.int = Ability(0)
        self.cha = Ability(0)
        # other
        self.ac = 0
        self.initiative = self.dex
        self.sc_ab = None
        self.starting_healing_spells = 0
        self.healing_spells = self.starting_healing_spells
        self.healing = None  # Normally dice object
        self.attacks = []
        self.hurtful = 0
        self.attack_parameters = []
        self.alt_attack = {}
        self.alignment = 'undeclared.'
        # internal stuff
        self.tally = {'damage': 0, 'hits': 0, 'dead': 0, 'misses': 0, 'battles': 0, 'rounds': 0, 'hp': 0,
                      'healing_spells': 0}
        self.copy_index = 1
        self.condition = 'normal'
        self.dodge = 0
        self.concentrating = 0
        self.temp = 0
        self.buff_spells = None
        self.conc_fx = None
        self.cr = 0
        self.custom = []
        self.hp = 0
        self.starting_hp = 0

    @property
    def abilities(self):
        """
        A fix to compensate how abilities are handled.
        Now they have their own attribute which is a die. With score and temp_modifier as extras

        :return:
        """
        return {n: getattr(self, n) for n in self.ability_names}

