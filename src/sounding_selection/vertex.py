from sounding_selection.point import Point


class Vertex(Point):
    """ A Vertex is an extension of Class Point and takes (x,y) attributes and an n number of field values."""
    def __init__(self, x, y, z, s57_type=None, s57_condition=None, catzoc=None, sounding_type=None):
        Point.__init__(self, x, y)
        self.__field_values = [z, s57_type, s57_condition, catzoc, sounding_type]

    @property
    def z_value(self):
        return self.__field_values[0]

    @z_value.setter
    def z_value(self, z):
        self.__field_values[0] = z

    @property
    def s57_type(self):
        return self.__field_values[1]

    @s57_type.setter
    def s57_type(self, feature):
        self.__field_values[1] = feature

    @property
    def s57_condition(self):
        return self.__field_values[2]

    @s57_condition.setter
    def s57_condition(self, condition):
        self.__field_values[2] = condition

    @property
    def catzoc_value(self):
        return self.__field_values[3]

    @catzoc_value.setter
    def catzoc_value(self, catzoc):
        self.__field_values[3] = catzoc

    @property
    def sounding_type(self):
        return self.__field_values[4]

    @sounding_type.setter
    def sounding_type(self, s_type):
        self.__field_values[4] = s_type

    def get_c(self, pos):
        if pos in (0, 1):
            return super().get_c(pos)
        else:
            try:
                return self.__field_values[pos]
            except IndexError as e:
                raise e

    def set_c(self, pos, c):
        if pos in (0, 1):
            super().set_c(pos, c)
        else:
            try:
                self.__field_values[pos] = c
            except IndexError:
                # Instead of raising an exception append the field value to the end of the array
                self.__field_values.append(c)

    def get_fields_num(self):
        return len(self.__field_values)

    def __str__(self):
        return "%s,%s,%s,%s,%s" % (self.x_value, self.y_value, self.z_value, self.catzoc_value, self.sounding_type)
