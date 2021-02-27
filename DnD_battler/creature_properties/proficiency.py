class Proficiency:

    def __init__(self, level:int, modifier: int):
        self.level = level
        self.modifier = modifier

    def get_bonus(self):
        return self.base_bonus + self.modifier

    @property
    def base_bonus(self):
        if self.level == 0:
            return 0
        else:
            return 2 + int((self.level - 1) / 4)

    def set_bonus(self, value):
        self.modifier = value - self.base_bonus

    bonus = property(get_bonus, set_bonus)
