from sounding_selection.domain import Domain


class TIN(object):
    """Creates Class TIN"""
    def __init__(self):
        self.__vertices = []
        self.__triangles = []
        self.__domain = Domain()

    def get_vertex(self, pos):
        try:
            return self.__vertices[pos]
        except IndexError as e:
            raise e

    def get_vertices_num(self):
        return len(self.__vertices)

    def get_triangle(self, pos):
        try:
            return self.__triangles[pos]
        except IndexError as e:
            raise e

    def get_triangles_num(self):
        return len(self.__triangles)

    def get_domain(self):
        return self.__domain

    def add_vertex(self, v):
        self.__vertices.append(v)

    def get_vertices(self):
        return self.__vertices

    def add_triangle(self, t):
        self.__triangles.append(t)

    def set_domain(self, min_p, max_p):
        self.__domain = Domain(min_p, max_p)
