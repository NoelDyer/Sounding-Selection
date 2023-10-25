class Point(object):
    """ Creates Class Point. """
    def __init__(self, x=0, y=0):
        """ Defines x and y Variables. """
        self.__coords = [x, y]

    # get functions series
    @property
    def x_value(self):
        return self.__coords[0]

    @x_value.setter
    def x_value(self, x):
        self.__coords[0] = x

    @property
    def y_value(self):
        return self.__coords[1]

    @y_value.setter
    def y_value(self, y):
        self.__coords[1] = y

    def get_c(self, pos):
        try:
            return self.__coords[pos]
        except IndexError as e:
            raise e

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
        return "Point(%s,%s)" % (self.x_value, self.y_value)
