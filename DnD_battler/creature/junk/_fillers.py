# inherited by CreatureAdvBase

from DnD_battler.creature._load_beastiary import CreatureLoader
from ._initialise import CreatureInitialise

class CreatureFill(CreatureLoader, CreatureInitialise):

    def _fill_from_dict(self, dictionary: dict):
        return self._initialise(**dictionary)

    def _fill_from_beastiary(self, name: str):
        if name in self.beastiary:
            return self._initialise(**self.beastiary[name])
        else:
            # For now fallback to preset. In future preset will be removed?
            return self._fill_from_preset(name)

    def _fill_from_preset(self, name:str):
        """
        Legacy... It might stop working due to code changes.
        :param name: the name of creature.
        :return: the stored creature.
        """
        if name == "netsharpshooter":
            self._initialise(name="netsharpshooter",
                             alignment="good",
                             hp=18, ac=18, hd=8,
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

