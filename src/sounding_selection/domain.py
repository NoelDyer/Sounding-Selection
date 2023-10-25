from sounding_selection.point import Point
from shapely.geometry import Polygon


class Domain(object):
    """Creates Class Domain"""

    def __init__(self, minimum=Point(), maximum=Point()):
        """Defines x and y variables"""
        self.__min = Point(minimum.x_value, minimum.y_value)
        self.__max = Point(maximum.x_value, maximum.y_value)

    def get_min_point(self):
        return self.__min

    def get_max_point(self):
        return self.__max

    def get_centroid(self):
        mid_x = self.__min.x_value + (self.__max.x_value - self.__min.x_value) / 2.0
        mid_y = self.__min.y_value + (self.__max.y_value - self.__min.y_value) / 2.0
        return Point(mid_x, mid_y)

    def contains_point(self, point, max_tin_point):
        """ Function takes type point and checks if the domain contains it """
        """ it considers as 'closed' only the edges incident in the lower left corner"""
        """ if the node-domain is on the border of tin-domain we consider as closed the
        corresponding sides having coordinates equal to the max-coordinate value"""
        for i in range(self.__min.get_coordinates_num()):
            if not self.coord_in_range(point.get_c(i), self.__min.get_c(i), self.__max.get_c(i), max_tin_point.get_c(i)):
                return False
        return True

    def intersects_polygon(self, polygon):
        node_rectangle = Polygon([(self.__min.x_value, self.__min.y_value),
                                  (self.__min.x_value, self.__max.y_value),
                                  (self.__max.x_value, self.__max.y_value),
                                  (self.__max.x_value, self.__min.y_value)])

        return polygon.intersects(node_rectangle)

    def contains_polygon(self, polygon):
        node_rectangle = Polygon([(self.__min.x_value, self.__min.y_value),
                                  (self.__min.x_value, self.__max.y_value),
                                  (self.__max.x_value, self.__max.y_value),
                                  (self.__max.x_value, self.__min.y_value)])

        return node_rectangle.contains(polygon)

    def coord_in_range(self, c, min_c, max_c, abs_max_c):
        if max_c == abs_max_c:
            if max_c < c:
                return False
        elif max_c <= c:
            return False
        if min_c > c:
            return False
        return True

    def contains_strict(self, point):
        """ Function takes type point and checks if the domain contains it """
        """ it considers as 'closed' all the edges of the domain """
        for i in range(self.__min.get_coordinates_num()):  # Update x and y coordinates
            if self.__max.get_c(i) < point.get_c(i) or self.__min.get_c(i) > point.get_c(i):
                return False
        return True

    def resize(self, point):  # Need to resize a Domain object only when reading a TIN file
        """ """
        if self.contains_strict(point):
            return
        for i in range(self.__min.get_coordinates_num()):  # Update x and y coordinates
            if point.get_c(i) < self.__min.get_c(i):
                self.__min.set_c(i, point.get_c(i))
            if point.get_c(i) > self.__max.get_c(i):
                self.__max.set_c(i, point.get_c(i))

    def contains_triangle(self, t, tin):
        for v_pos in range(t.get_vertices_num()):
            if self.contains_point(tin.get_vertex(t.get_tv(v_pos)), tin.get_domain().get_max_point()):
                return True
        return False

    def __str__(self):
        return "Domain(%s,%s)" % (self.__min, self.__max)
