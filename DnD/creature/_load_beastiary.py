# inherited by CreatureFiller

import csv, warnings

class CreatureLoader:

    beastiary = None

    @classmethod
    def load_beastiary(cls, path):
        """
        beastiary is the Monster Manual, minus the copyrighted creatures.

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
            r = csv.reader(open(path, encoding='utf-8'))
            headers = next(r)
            beastiary = {}
            for line in r:
                beast = {h: line[i] for i, h in enumerate(headers) if line[i]}
                if 'name' in beast:
                    beastiary[beast['name']] = beast
            cls.beastiary = beastiary
            return beastiary
        except Exception as e:
            warnings.warn('Beastiary error, expected path ' + path + ' error ' + str(e))
            return {}

# ------------- Load ----------------------------------------------------------------------

CreatureLoader.load_beastiary('beastiary.csv')
