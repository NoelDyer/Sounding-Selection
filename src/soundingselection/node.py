from domain import Domain
from point import Point

# sons legend:
#   ne = 0
#   nw = 1
#   sw = 2
#   se = 3


class Node(object):
    ''' Creates Class node '''
    def __init__(self):
        self.__vertex_ids = list()  # indices of points
        self.__sons = None

    def add_vertex(self, id):
        self.__vertex_ids.append(id)

    def remove_vertex(self, id):
        self.__vertex_ids.remove(id)

    def init_sons(self):
        self.__sons = [Node() for _ in range(4)]

    def get_son(self, i):
        return self.__sons[i]

    def is_leaf(self):
        return self.__sons == None

    def get_vertices(self):
        return self.__vertex_ids

    def get_vertices_num(self):
        return len(self.__vertex_ids)

    def reset_vertices(self):
        self.__vertex_ids = list()

    def overflow(self, capacity):
        return len(self.__vertex_ids) > capacity

    def compute_son_label_and_domain(self, son_position, node_label, node_domain, mid_point):
        if son_position == 0:  # "ne":
            return 4*node_label+1,Domain(mid_point, node_domain.get_max_point())
        elif son_position == 1:  # "nw":
            min = Point(node_domain.get_min_point().get_x(), mid_point.get_y())
            max = Point(mid_point.get_x(), node_domain.get_max_point().get_y())
            return 4*node_label+2,Domain(min, max)
        elif son_position == 2:  # "sw":
            return 4*node_label+3,Domain(node_domain.get_min_point(), mid_point)
        elif son_position == 3:  # "se":
            min = Point(mid_point.get_x(), node_domain.get_min_point().get_y())
            max = Point(node_domain.get_max_point().get_x(), mid_point.get_y())
            return 4*node_label+4,Domain(min, max)
        else:
            return None, None

    def is_duplicate(self, v_index, tin):
        for i in self.get_vertices():
            if tin.get_vertex(i) == tin.get_vertex(v_index):
                return True
        return False
