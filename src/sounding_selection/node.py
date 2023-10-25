from sounding_selection.domain import Domain
from sounding_selection.point import Point
from sounding_selection.cartographic_model import get_carto_symbol
from sounding_selection.catzoc import *
from shapely.geometry import Point as Shapely_Point
from shapely.geometry import Polygon
import queue


# sons legend:
#   ne = 0
#   nw = 1
#   sw = 2
#   se = 3


class Node(object):
    """ Creates Class node """
    def __init__(self):
        self.__vertex_ids = list()  # indices of points
        self.__triangle_ids = list()  # Indices of triangles
        self.__sons = None

    def add_vertex(self, v_id):
        self.__vertex_ids.append(v_id)

    def remove_vertex(self, v_id):
        self.__vertex_ids.remove(v_id)

    def get_vertices(self):
        return self.__vertex_ids

    def get_vertices_num(self):
        return len(self.__vertex_ids)

    def reset_vertices(self):
        self.__vertex_ids = list()

    def add_triangle(self, t_id):
        self.__triangle_ids.append(t_id)

    def get_triangles(self):
        return self.__triangle_ids

    def get_triangles_num(self):
        return len(self.__triangle_ids)

    def init_sons(self):
        self.__sons = [Node() for _ in range(4)]

    def get_son(self, i):
        return self.__sons[i]

    def is_leaf(self):
        return self.__sons is None

    def overflow(self, capacity):
        return len(self.__vertex_ids) > capacity

    @staticmethod
    def compute_son_label_and_domain(son_position, node_label, node_domain, mid_point):
        if son_position == 0:  # "ne":
            return 4*node_label+1, Domain(mid_point, node_domain.get_max_point())
        elif son_position == 1:  # "nw":
            minimum = Point(node_domain.get_min_point().x_value, mid_point.y_value)
            maximum = Point(mid_point.x_value, node_domain.get_max_point().y_value)
            return 4*node_label+2, Domain(minimum, maximum)
        elif son_position == 2:  # "sw":
            return 4*node_label+3, Domain(node_domain.get_min_point(), mid_point)
        elif son_position == 3:  # "se":
            minimum = Point(mid_point.x_value, node_domain.get_min_point().y_value)
            maximum = Point(node_domain.get_max_point().x_value, mid_point.y_value)
            return 4*node_label+4, Domain(minimum, maximum)
        else:
            return None, None

    def is_duplicate(self, v_index, tin):
        for i in self.get_vertices():
            if tin.get_vertex(i) == tin.get_vertex(v_index):
                return True
        return False

    def extract_vertex_vertex(self, tin):
        vvs = [set() for _ in self.get_vertices()]
        for t_id in self.get_triangles():
            t = tin.get_triangle(t_id)
            for v_id in range(t.get_vertices_num()):
                if t.get_tv(v_id) in self.get_vertices():
                    v_pos = self.get_vertices().index(t.get_tv(v_id))
                    vvs[v_pos].add(t.get_tv((v_id+1) % t.get_vertices_num()))
                    vvs[v_pos].add(t.get_tv((v_id+2) % t.get_vertices_num()))

        return vvs

    def extract_vertex_triangle(self, tin):
        vts = [list() for _ in self.get_vertices()]
        for t_id in self.get_triangles():
            t = tin.get_triangle(t_id)
            for v_id in range(t.get_vertices_num()):
                if t.get_tv(v_id) in self.get_vertices():
                    v_pos = self.get_vertices().index(t.get_tv(v_id))
                    vts[v_pos].append(t_id)
        return vts

    def carto_model_generalization(self, target_v, point_set, delete_list, scale, h_spacing, v_spacing):
        deletes = {}
        for v_id in self.get_vertices():
            v = point_set.get_vertex(v_id)
            if v != target_v:
                if target_v.s57_type is None:
                    target_symbol = get_carto_symbol(target_v, scale, h_spacing, v_spacing)[1]
                    v_symbol = get_carto_symbol(v, scale, h_spacing, v_spacing)[1]
                    if target_symbol.intersects(v_symbol) and target_v.z_value <= v.z_value:
                        # z-value precision issue: use '<=' to remove initial legibility violations
                        deletes[v_id] = v
                else:
                    target_symbol = get_carto_symbol(target_v, scale, 0, 0)[1]
                    v_symbol = get_carto_symbol(v, scale, 0, 0)[1]
                    if target_symbol.intersects(v_symbol):
                        deletes[v_id] = v

        for v_id in deletes:
            delete_list.append(deletes[v_id])
            self.remove_vertex(v_id)

        return

    def radius_based_generalization(self, target_v, point_set, delete_list, radius_lookup):
        radius_length = radius_lookup[target_v.__str__()]
        circle = Shapely_Point(target_v.x_value, target_v.y_value).buffer(radius_length)
        deletes = {}
        for v_id in self.get_vertices():
            v = point_set.get_vertex(v_id)
            if v != target_v:
                s_point = Shapely_Point(v.x_value, v.y_value)
                if circle.intersects(s_point) and target_v.z_value <= v.z_value:
                    # z-value precision issue: use '<=' to remove legibility violations
                    deletes[v_id] = v

        for v_id in deletes:
            delete_list.append(deletes[v_id])
            self.remove_vertex(v_id)

        return

    def extract_fill_soundings(self, tin, point_set, point_tree, fill_soundings):
        catzoc_dict = {1: 'A1',
                       2: 'A2',
                       3: 'B',
                       4: 'C',
                       5: 'D',
                       6: 'U'}

        for t_id in self.get_triangles():
            tri = tin.get_triangle(t_id)
            tri_points = list()
            for v in range(tri.get_vertices_num()):
                v_id = tri.get_tv(v)
                tri_points.append(tin.get_vertex(v_id))

            triangle, z_vals, catzoc_values = list(), list(), list()
            for point in tri_points:
                triangle.append([point.x_value, point.y_value])
                z_vals.append(point.z_value)
                catzoc_values.append(point.catzoc_value)

            # Use the highest quality catzoc of the triangle
            catzoc_sorted = sorted([c for c in catzoc_values if c is not None])
            if len(catzoc_sorted) > 0:
                best_catzoc = catzoc_sorted[0]
                catzoc = catzoc_dict[best_catzoc]
            else:
                catzoc = catzoc_dict[6]

            # Skip triangles along boundary; cannot assess triangles with no depth tolerance
            if float(-99999) not in z_vals and catzoc != 'U' and catzoc != 'D':
                intersect_triangle_list = list()
                point_tree.points_in_polygon(point_tree.get_root(), 0, point_set.get_domain(), Polygon(triangle),
                                             point_set, intersect_triangle_list)

                inside_triangle_list = [v for v in intersect_triangle_list if v not in tri_points]

                difference_list = list()
                for v in inside_triangle_list:
                    p1, p2, p3 = tri_points[0], tri_points[1], tri_points[2]
                    weight1_numer = ((p2.y_value - p3.y_value) * (v.x_value - p3.x_value)) + \
                                    ((p3.x_value - p2.x_value) * (v.y_value - p3.y_value))

                    weight2_numer = ((p3.y_value - p1.y_value) * (v.x_value - p3.x_value)) + \
                                    ((p1.x_value - p3.x_value) * (v.y_value - p3.y_value))

                    denom = ((p2.y_value - p3.y_value) * (p1.x_value - p3.x_value)) + \
                            ((p3.x_value - p2.x_value) * (p1.y_value - p3.y_value))

                    weight1 = weight1_numer / denom
                    weight2 = weight2_numer / denom
                    weight3 = 1 - weight1 - weight2

                    interp_z = (p1.z_value * weight1) + (p2.z_value * weight2) + (p3.z_value * weight3)
                    actual_z = v.z_value

                    if abs(interp_z - actual_z) > depth_tolerance(catzoc, actual_z):
                        difference_list.append([v, interp_z - actual_z])

                # Identify soundings with largest difference
                if len(difference_list) > 0:
                    diff_sorted = sorted(difference_list, key=lambda k: k[1], reverse=True)
                    fill = diff_sorted[0][0]
                    if fill not in fill_soundings:
                        fill_soundings.append(fill)
        return

    def points_in_polygon(self, polygon, point_set, point_list):
        for v_id in self.get_vertices():
            v = point_set.get_vertex(v_id)
            s_point = Shapely_Point(v.x_value, v.y_value)
            if polygon.intersects(s_point):
                point_list.append(v)
        return

    def compute_crit(self, tin):
        if self.is_leaf():
            vts = self.extract_vertex_triangle(tin)
            vvs = self.extract_vertex_vertex(tin)
            for i in range(self.get_vertices_num()):
                upper, lower = dict(), dict()
                vid = self.get_vertices()[i]
                v = tin.get_vertex(vid)
                vv = vvs[i]
                into_flat_area = False
                for vid2 in vv:
                    v2 = tin.get_vertex(vid2)
                    if v.z_value > v2.z_value:
                        lower[vid2] = vid2
                    elif v.z_value < v2.z_value:
                        upper[vid2] = vid2
                    else:
                        into_flat_area = True
                        break

                if into_flat_area is False:
                    if len(upper) == 0:
                        v.sounding_type = 'Minima'
                    elif len(lower) == 0:
                        v.sounding_type = 'Maxima'
                    else:
                        uc_num, lc_num = init_adjacent_vertices(vid, v, vts[i], tin, upper, lower)
                        if uc_num >= 2 and lc_num >= 2:
                            v.sounding_type = 'Saddle'


def init_adjacent_vertices(vid, v, vt, tin, upper, lower):
    adj_upper = dict()
    adj_lower = dict()
    for tid in vt:
        t = tin.get_triangle(tid)
        for i in range(0, 3):
            if t.get_tv(i) == vid:
                v_pos = i
                break
        e = [t.get_tv((v_pos+1) % 3), t.get_tv((v_pos+2) % 3)]
        if v.z_value < tin.get_vertex(e[0]).z_value and v.z_value < tin.get_vertex(e[1]).z_value:
            if e[0] not in adj_upper:
                adj_upper[e[0]] = {e[1]}
            else:
                adj_upper[e[0]].add(e[1])
            if e[1] not in adj_upper:
                adj_upper[e[1]] = {e[0]}
            else:
                adj_upper[e[1]].add(e[0])
        if v.z_value > tin.get_vertex(e[0]).z_value and v.z_value > tin.get_vertex(e[1]).z_value:
            if e[0] not in adj_lower:
                adj_lower[e[0]] = {e[1]}
            else:
                adj_lower[e[0]].add(e[1])
            if e[1] not in adj_lower:
                adj_lower[e[1]] = {e[0]}
            else:
                adj_lower[e[1]].add(e[0])
    uc_num = get_components_num(adj_upper, upper)
    lc_num = get_components_num(adj_lower, lower)
    return uc_num, lc_num


def get_components_num(adj_map, v_flag):
    for adj in adj_map:
        if adj == v_flag[adj]:
            flag = v_flag[adj]
            q = queue.Queue()
            q.put(adj)
            while not q.empty():
                current = q.get()
                if v_flag[current] == current:
                    v_flag[current] = flag
                    adj_cur = adj_map[current]
                    for a in adj_cur:
                        q.put(a)
    components = set()
    for i in v_flag:
        components.add(v_flag[i])
    return len(components)
