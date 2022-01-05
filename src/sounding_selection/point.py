class Point(object):
    """Creates Class Point."""
    def __init__(self, x=0, y=0):
        """Defines x and y variables"""
        self.__coords = [x, y]

    # get functions series
    def get_x(self):
        return self.__coords[0]

    def get_y(self):
        return self.__coords[1]

    def get_c(self, pos):
        try:
            return self.__coords[pos]
        except IndexError as e:
            raise e

    # set functions series
    def set_x(self, x):
        self.__coords[0] = x

    def set_y(self, y):
        self.__coords[1] = y

    def set_c(self, pos, c):
        try:
            self.__coords[pos] = c
        except IndexError as e:
            # here we don't append a new coordinate at the end as a point is a fixed 2D entity
            raise e

    def get_coordinates_num(self):
        return len(self.__coords)

    def __eq__(self, other):
        return self.__coords[0] == other.__coords[0] and self.__coords[1] == other.__coords[1]

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "Point(%s,%s)" % (self.get_x(), self.get_y())
