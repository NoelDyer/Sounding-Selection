from domain import Domain


class PointSet(object):

    def __init__(self):
        self.__vertices = []
        self.__domain = Domain()

    def get_vertex(self, pos):
        try:
            return self.__vertices[pos]
        except IndexError as e:
            raise e

    def get_vertices_num(self):
        return len(self.__vertices)

    def get_all_vertices(self):
        return self.__vertices

    def get_domain(self):
        return self.__domain

    def add_vertex(self, v):
        self.__vertices.append(v)

    def remove_vertex(self, v):
        self.__vertices.remove(v)

    def set_domain(self, min_p, max_p):
        self.__domain = Domain(min_p, max_p)
