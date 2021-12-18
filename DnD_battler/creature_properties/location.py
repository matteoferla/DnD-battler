## Unfinished

from .size import Size

class Location:

    def __init__(self, size: Size, x:int=0, y:int=0):
        self.size = size
        self.x = 0
        self.y = 0
        self.map = None

    def move(self, dx:int=0, dy:int=0):
        self.x += dx
        self.y += dy

class Map:
    pass

# rock

