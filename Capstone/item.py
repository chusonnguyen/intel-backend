"""
2D Item class.
"""
#from ctypes.wintypes import INT


class Item:
    """
    Items class for rectangles inserted into sheets
    """
    def __init__(self, width, height, name :str,
                 CornerPoint: tuple = (0, 0),
                 rotation: bool = True) -> None:
        self.width = width
        self.height = height
        self.name = name
        self.x = CornerPoint[0]
        self.y = CornerPoint[1]
        self.area = self.width * self.height
        self.rotated = False
        self.id = 0


    def __repr__(self):
        return 'Item(name=%r width=%r, height=%r, x=%r, y=%r)' % (self.name, self.width, self.height, self.x, self.y)


    def rotate(self) -> None:
        self.width, self.height = self.height, self.width
        self.rotated = False if self.rotated == True else True

