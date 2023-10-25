from sounding_selection.node import Node
from sounding_selection.cartographic_model import *
from sounding_selection.catzoc import *
from shapely.geometry import Point, Polygon


class Tree(object):
    """Creates Class Tree"""
    def __init__(self, c):
        self.__root = Node()
        self.__capacity = c

    def get_root(self):
        return self.__root

    def get_leaf_threshold(self):
        return self.__capacity

    def build_point_tree(self, point_set):
        for i in range(point_set.get_vertices_num()):
            self.insert_vertex(self.__root, 0, point_set.get_domain(), i, point_set)

    def build_tin_tree(self, tin):
        # First insert the vertices of the TIN
        for i in range(tin.get_vertices_num()):
            self.insert_vertex(self.__root, 0, tin.get_domain(), i, tin)
        # Then triangles
        for i in range(tin.get_triangles_num()):
            self.insert_triangle(self.__root, 0, tin.get_domain(), i, tin)

    def insert_vertex(self, node, node_label, node_domain, v_index, tin):
        if node_domain.contains_point(tin.get_vertex(v_index), tin.get_domain().get_max_point()):
            if node.is_leaf():
                if node.is_duplicate(v_index, tin):
                    return
                node.add_vertex(v_index)  # update append list
                if node.overflow(self.__capacity):
                    node.init_sons()
                    for i in node.get_vertices():
                        self.insert_vertex(node, node_label, node_domain, i, tin)
                    node.reset_vertices()  # empty the list of the current node

            else:  # Internal
                mid_point = node_domain.get_centroid()
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    self.insert_vertex(node.get_son(i), s_label, s_domain, v_index, tin)

    def insert_triangle(self, node, node_label, node_domain, triangle_id, tin):
        tri = tin.get_triangle(triangle_id)
        if node_domain.contains_triangle(tri, tin):
            if node.is_leaf():
                node.add_triangle(triangle_id)  # Update index list

            else:  # Internal
                mid_point = node_domain.get_centroid()
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    self.insert_triangle(node.get_son(i), s_label, s_domain, triangle_id, tin)

    def generalization(self, node, node_label, node_domain, target_v, point_set, delete_list, algorithm, scale=None,
                       h_spacing=None, v_spacing=None, radius_lookup=None):

        if node is None:
            return
        else:
            if node.is_leaf():
                if node.get_vertices_num() == 0:
                    pass
                else:
                    if algorithm is 'DCM':
                        node.carto_model_generalization(target_v, point_set, delete_list, scale, h_spacing, v_spacing)
                    else:
                        node.radius_based_generalization(target_v, point_set, delete_list, radius_lookup)

            else:  # Internal
                # Visit the sons in the following order: NE -> NW -> SW -> SE
                mid_point = node_domain.get_centroid()
                if algorithm is 'DCM':
                    search_window = get_carto_symbol(target_v, scale, h_spacing, v_spacing)[0]
                else:
                    radius_length = radius_lookup[target_v.__str__()]
                    search_window = Point(target_v.x_value, target_v.y_value).buffer(radius_length)
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    if s_domain.contains_polygon(search_window):
                        self.generalization(node.get_son(i), s_label, s_domain, target_v, point_set, delete_list,
                                            algorithm, scale, h_spacing, v_spacing, radius_lookup)
                        break
                    elif s_domain.intersects_polygon(search_window):
                        self.generalization(node.get_son(i), s_label, s_domain, target_v, point_set, delete_list,
                                            algorithm, scale, h_spacing, v_spacing, radius_lookup)

    def points_in_polygon(self, node, node_label, node_domain, polygon, point_set, point_list):
        if node is None:
            return
        else:
            if node.is_leaf():
                if node.get_vertices_num() == 0:
                    pass
                else:
                    node.points_in_polygon(polygon, point_set, point_list)
            else:
                mid_point = node_domain.get_centroid()
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    if s_domain.contains_polygon(polygon):
                        self.points_in_polygon(node.get_son(i), s_label, s_domain, polygon, point_set, point_list)
                        break
                    if s_domain.intersects_polygon(polygon):
                        self.points_in_polygon(node.get_son(i), s_label, s_domain, polygon, point_set, point_list)

    def crit_query(self, node, node_label, node_domain, tin):
        if node.is_leaf():
            # Extract the VV topological relation for all the indexed vertices
            node.compute_crit(tin)
        else:  # Internal
            # we visit the sons in the following order: NE -> NW -> SW -> SE
            mid_point = node_domain.get_centroid()
            for i in range(4):
                s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                self.crit_query(node.get_son(i), s_label, node_domain, tin)

    def calculate_fill_soundings(self, node, node_label, node_domain, point_tree, point_set, tin, fill_soundings):

        if node is None:
            return
        else:
            if node.is_leaf():
                if node.get_vertices_num() == 0 and node.get_triangles_num() == 0:
                    pass
                else:
                    node.extract_fill_soundings(tin, point_set, point_tree, fill_soundings)

            else:  # Internal
                # we visit the sons in the following order: NE -> NW -> SW -> SE
                mid_point = node_domain.get_centroid()
                for i in range(4):
                    s_label, s_domain = node.compute_son_label_and_domain(i, node_label, node_domain, mid_point)
                    self.calculate_fill_soundings(node.get_son(i), s_label, s_domain, point_tree, point_set, tin,
                                                  fill_soundings)
