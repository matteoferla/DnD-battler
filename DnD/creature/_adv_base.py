from ._fillers import CreatureFill
import warnings

class CreatureAdvBase(CreatureFill):


    def __init__(self, wildcard, **kwargs):  # I removed *args... not sure what they did.
        """
        Creature object creation. A lot of paramaters make a creature so a lot of assumptions are made (see __init__`).

        :param wildcard: the name of the creature.
          If nothing else is passed it will take it from the beastiary.
          If a dictionary is passed, it will process it like **kwargs,
          If a Creature object is passed it will make a copy
        :param kwargs: a lot of arguments...
        :return: a creature.

        The arguments are many...

        >>> print(Creature(Creature('aboleth'), ac=20).__dict__)

            {'abilities': None,
             'dex': 10,
             'con_bonus': 10,
             'cr': 17,
             'xp': 5900,
             'ac': 20,
             'starting_healing_spells': 0,
             'starting_hp': 135,
             'condition': 'normal',
             'initiative': 'Dice.num_faces',
             'str': 10,
             'wis': 10,
             'ability_bonuses': {'int': 0,
              'cha': 0,
              'dex': 0,
              'con': 0,
              'str': 0,
              'wis': 0},
             'custom': [],
             'hd': 'Dice',
             'hurtful': 36.0,
             'tally': {'rounds': 0,
              'hp': 0,
              'battles': 0,
              'hits': 0,
              'damage': 0,
              'healing_spells': 0,
              'dead': 0,
              'misses': 0},
             'hp': 135,
             'proficiency': 5,
             'cha_bonus': 10,
             'able': 1,
             'healing_spells': 0,
             'copy_index': 1,
             'int': 10,
             'concentrating': 0,
             'wis_bonus': 10,
             'con': 10,
             'int_bonus': 10,
             'sc_ab': 'con',
             'str_bonus': 10,
             'level': 18,
             'settings': {},
             'arena': None,
             'dex_bonus': 10,
             'log': '',
             'cha': 10,
             'dodge': 0,
             'alt_attack': {'attack': None, 'name': None},
             'alignment': 'lawful evil ',
             'attacks': [{'attack': 'Dice', 'damage': 'Dice', 'name': 'tentacle'},
              {'attack': 'Dice', 'damage': 'Dice', 'name': 'tentacle'},
              {'attack': 'Dice', 'damage': 'Dice', 'name': 'tentacle'}],
             'attack_parameters': [['tentacle', 9, 5, 6, 6],
              ['tentacle', 9, 5, 6, 6],
              ['tentacle', 9, 5, 6, 6]],
             'buff_spells': 0,
             'temp': 0,
             'name': 'aboleth'}
        """
        super().__init__()
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
        elif type(wildcard) is self.__class__:
            self._initialise(base=wildcard, **kwargs)
        else:
            warnings.warn("UNKNOWN COMBATTANT:" + str(wildcard))
            # raise Exception
            print("I will not raise an error. I will raise Cthulhu to punish this user errors")
            self._fill_from_preset("cthulhu")
