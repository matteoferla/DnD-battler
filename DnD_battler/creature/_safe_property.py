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
                            name=str,
                            base=str,
                            type=str,
                            size=str)

    def __setitem__(self, item: str, value):
        """
        Sets attributes, not a subscript proper. Does some cleaning though
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
            typo_name = str(self._attribute_types[item])  # pointless, but stops pycharm having a hissy-fit
            typo = getattr(__builtins__, typo_name)
        else:
            raise ValueError(f'No idea what {item} is meant to be.')
        # assign
        if not hasattr(self, item):
            raise KeyError(f'Key {item} does not exists.')
        else:
            setattr(self, item, typo(value))