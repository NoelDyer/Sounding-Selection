from sounding_selection.point import Point
from shapely.geometry import Polygon


class Domain(object):
    """Creates Class Domain"""

    def __init__(self, min=Point(), max=Point()):
        """Defines x and y variables"""
        self.__min = Point(min.get_x(), min.get_y())
        self.__max = Point(max.get_x(), max.get_y())

    def get_min_point(self):
        return self.__min

    def get_max_point(self):
        return self.__max

    def get_centroid(self):
        mid_x = self.__min.get_x() + (self.__max.get_x()-self.__min.get_x())/2.0
        mid_y = self.__min.get_y() + (self.__max.get_y()-self.__min.get_y())/2.0
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

    def polygon_intersect(self, polygon):
        # polygon = Polygon(vertex_list)
        node_rectangle = Polygon([(self.__min.get_x(), self.__min.get_y()),
                                  (self.__min.get_x(), self.__max.get_y()),
                                  (self.__max.get_x(), self.__max.get_y()),
                                  (self.__max.get_x(), self.__min.get_y())])

        return polygon.intersects(node_rectangle)

    def polygon_contains(self, polygon):
        # polygon = Polygon(vertex_list)
        node_rectangle = Polygon([(self.__min.get_x(), self.__min.get_y()),
                                  (self.__min.get_x(), self.__max.get_y()),
                                  (self.__max.get_x(), self.__max.get_y()),
                                  (self.__max.get_x(), self.__min.get_y())])

        return node_rectangle.contains(polygon)

    def polygon_touches(self, polygon):
        # polygon = Polygon(vertex_list)
        node_rectangle = Polygon([(self.__min.get_x(), self.__min.get_y()),
                                  (self.__min.get_x(), self.__max.get_y()),
                                  (self.__max.get_x(), self.__max.get_y()),
                                  (self.__max.get_x(), self.__min.get_y())])

        return node_rectangle.touches(polygon)

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

    def contains_vertex(self, vertex):
        """ Function takes type vertex and checks if the domain contains it """
        """ it considers as 'closed' all the edges of the domain """
        for i in range(self.__min.get_coordinates_num()):
            if self.__max.get_c(i) < vertex.get_c(i) or self.__min.get_c(i) > vertex.get_c(i):
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
            if self.contains_point(tin.get_vertex(t.get_TV(v_pos)), tin.get_domain().get_max_point()):
                return True
        return False

    def __str__(self):
        return "Domain(%s,%s)" % (self.__min, self.__max)
