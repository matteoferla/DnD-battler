#from ._fillers import CreatureFill
from ._load_beastiary import CreatureLoader
from ._init_abilities import CreatueInitAble
from ._safe_property import CreatureSafeProp
from ._level import CreatureLevel
from ..dice import AbilityDie, AttackRoll

class CreatureAdvBase(CreatueInitAble, CreatureSafeProp, CreatureLoader, CreatureLevel):

    def __init__(self, **settings):
        super().__init__()
        self.apply_settings(**settings)

    @classmethod
    def load(cls, creature_name, **settings):
        """
        Loads from MM

        :param creature_name:
        :return:
        """
        cleaned = lambda name: name.lower().replace('_', ' ')
        if creature_name in cls.beastiary:
            self = cls(**cls.beastiary[creature_name])
        elif cleaned(creature_name) in cls.beastiary:
            self = cls(**cls.beastiary[cleaned(creature_name)])
        else:
            raise ValueError(f'Creature "{creature_name}" not found.')
        self.base = creature_name
        self.apply_settings(**settings)
        return self

    def apply_settings(self, **settings):
        settings = {k.lower(): v for k, v in settings.items()}
        # -------------- assign fluff values ---------------------------------------------------------------------------
        for key in ('name', 'base', 'type', 'size', 'alignment'):
            if key in settings:
                self[key] = settings[key]
        for key in ('xp', 'hp'):
            if key in settings:
                self[key] = settings[key]
        # -------------- set complex values ----------------------------------------------------------------------------
        # abilities
        self.set_ability_dice(**settings)
        # arena
        if 'arena' in settings:
            self.arena = settings['arena']
        # level
        if 'level' in settings:
            self.set_level(**settings)
        # proficiency
        if 'proficiency' in settings:
            self.proficiency.bonus = int(settings['proficiency'])
        # hit dice
        if 'hd' in settings:
            self.hit_die.num_faces = [int(settings['hd'])]
            if 'hp' not in settings:
                self.recalculate_hp()
        # other
        if 'sc_ability' in settings:
            sc_a = settings['sc_ability'].lower()
            assert sc_a in self.ability_names, f'{sc_a} is not a valid ability name {self.ability_names}'
            self.spellcasting_ability_name = sc_a
        # ac
        self.set_ac(**settings)
        if 'initiative_bonus' in settings:
            self.initiative.modifier = int(settings['initiative_bonus'])
        # attacks
        if 'attack_parameters' in settings or 'attacks' in settings:
            self.attacks = self.parse_attacks(**settings)