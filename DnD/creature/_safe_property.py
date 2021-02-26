from ._base import CreatureBase

class CreatureSafeProp(CreatureBase):

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            raise KeyError(f'Key {item} does not exists.')

    # prevent weird values being passed in settings and __setitem__
    _attribute_types = dict(level=int,
                            custom=list,
                            xp=int,
                            proficiency=int)

    def __setitem__(self, item: str, value):
        """
        Sets attributes, not a subscript proper.
        It sets it only if there not one in ``self.settings``
        Basically if you want to set a value of say ``self.proficiency`` assign it normally

        >>> self.proficiency =999

        If you want it as a backup to a value of ``self.settings`` (blanked on completed init)

        >>> self['proficiency'] = 69

        formerly _set.

        Corrects the value to a known type if of known, thanks to self._attribute_types
        For historical reasons it accepts the types as str. (shudder)

        :param item: an attribute of self
        :param value:
        :return:
        """
        # get type adaptor
        if item not in self._attribute_types:
            #typo = str
            typo = lambda v: v  # do nothing.
        elif isinstance(self._attribute_types[item], type):
            typo = self._attribute_types[item] # normal class.
        elif isinstance(self._attribute_types[item], str): # string name of class. Yuck.
            typo = getattr(__builtins__, self._attribute_types[item])
        else:
            raise ValueError(f'No idea what {item} is meant to be.')
        # assign
        if not hasattr(self, item):
            raise KeyError(f'Key {item} does not exists.')
        elif item in self.settings:
            setattr(self, item, typo(self.settings[item]))
        else:
            setattr(self, item, typo(value))

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
        if not old_level:  # zero???
            self.hp = 0
            self.hd.crit = 1  # Not-RAW first level is always max for PCs, but not monsters.
            for x in range(level):
                self.hp += self.hd.roll()
        else:
            for x in range(level - old_level):
                self.hp += self.hd.roll()
        self.level = level
        self.starting_hp = self.hp
        self.proficiency = 1 + round((self.level) / 4)
        if hasattr(self, 'attacks'):
            for attack in self.attacks:
                attack['attack'].bonus += self.proficiency - 1 + round((old_level) / 4)
                # Changing by delta proficiency as there is no way of knowing what weapon bonuses there may be etc.