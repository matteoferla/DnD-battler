from typing import *

class Size:
    """
    This is a fake enum.
    Enums are immutable. which is bad here as enlarge and shrink would not be usable (as a new instance would be made).

    However in 5e size does not affect Abilities or AC (cough cough... it does in the monster stats but shh)
    """
    space_map = dict(fine=0.5,
                     diminutive=1,
                     tiny=2.5,
                     small=5,
                     medium=5,
                     large=10,
                     huge=15,
                     gargantuan=20,
                     colossal=64)

    @property
    def size_options(self) -> List[str]:
        # this is generated from space_map
        return list(self.space_map.keys())

    @property
    def value(self) -> int:  # fake enum
        return self.size_options.index(self.name)

    def __init__(self, size: Union[int, str]):
        if isinstance(size, int):
            self.name = self.size_options[size]
        elif isinstance(size, str):
            assert size in self.size_options, f'{size} not a valid size {self.size_options}'
            self.name = size
        else:
            raise TypeError(f'size {size} is not str|int')

    @property
    def space(self) -> float:
        return self.space_map[self.name]

    def enlarge(self):
        if self.name == 'colossal':
            pass
        self.name = self.size_options[self.value + 1]

    def shrink(self):
        if self.name == 'fine':
            pass
        self.name = self.size_options[self.value - 1]
