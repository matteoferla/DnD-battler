from .errors import ActionError

class Action:
    """
    Remember to override: ``do``, ``absolute_score``, ``find_targets``, ``activatable``.
    """
    def __init__(self, creature: 'Creature', name : str, typology: Union[str, AttackType] = 'melee', **kwargs):
        self.creature = creature
        self.log = self.creature.log
        self.name = name
        self.type = self._parse_type(typology)

    def do(self):
        pass

    def _parse_type(self, typology: Union[str, AttackType]):
        if isinstance(typology, AttackType):
            return typology
        elif isinstance(typology, str):
            return AttackType[typology]
        else:
            raise TypeError

    # ------------ Target ----------------------------------------------------------------------------------------------

    def find_targets(self) -> 'Creature':
        """
        Method to be overridden
        """
        return [self.creature]

    def find_target(self, valid:bool=True):
        """
        calls ``self.find_targets`` and ``self.is_valid_target``

        :param valid: filter by valid per self.is_valid_target
        :return:
        """
        for target in self.find_targets():
            if not valid:
                return target
            elif self.is_valid_target(target):
                return target
            else:
                pass  # not good target.
        else:
            raise ActionError

    # ------------ Score -----------------------------------------------------------------------------------------------
    # Decision making: how good is this action and can it be run?

    def score(self) -> float:
        """
        Decision making: how good is this action?
        :return:
        """
        if self.activatable():
            return self.absolute_score()
        else:
            return 0

    def absolute_score(self):
        return 1

    def activatable(self):
        """
        Can this action be run?
        :return:
        """
        if self.creature.condition in ('incapacitated', 'unconscious', 'stunned', 'petrified', 'paralyzed'):
            return False
        else:
            return True