from point import Point


class Vertex(Point):
    """ A Vertex is an extension of Class Point and takes (x,y) attributes plus an elevation."""
    def __init__(self, x, y, z):
        Point.__init__(self, x, y)
        self.__field_values = [z]  # default.. a vertex has one field value... it can be extended though!

    def get_z(self):
        return self.__field_values[0]

    def set_z(self,z):
        self.__field_values[0] = z

    def get_c(self,pos):
        if pos in (0,1):
            return super().get_c(pos)
        else:
            try:
                return self.__field_values[pos]
            except IndexError as e:
                raise e

    def set_c(self,pos,c):
        if pos in (0,1):
            super().set_c(pos,c)
        else:
            try:
                self.__field_values[pos] = c
            except IndexError as e:
                # raise e
                # instead of raising an exception we append the field value to the end of the array
                self.__field_values.append(c)

    def get_fields_num(self):
        return len(self.__field_values)

    def __str__(self):
        return "%s,%s,%s" % (self.get_x(), self.get_y(), self.get_z())
