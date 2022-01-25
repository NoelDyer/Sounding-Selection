from sounding_selection.characterdimensions import get_character_dimensions
from shapely.geometry import Polygon


def validate_functionality_constraint(generalized_tin, source_tree, source_point_set, scale, h_spacing, v_spacing):
    safety_violations = list()

    for t_id in range(generalized_tin.get_triangles_num()):
        tri = generalized_tin.get_triangle(t_id)
        tri_points = list()
        for v in range(tri.get_vertices_num()):
            v_id = tri.get_TV(v)
            tri_points.append(generalized_tin.get_vertex(v_id))

        z_vals, triangle = list(), list()
        for point in tri_points:
            z_vals.append(point)
            triangle.append([point.get_x(), point.get_y()])

        point_list = list()
        source_tree.get_points_in_polygon(source_tree.get_root(), 0, source_point_set.get_domain(),
                                          Polygon(triangle), source_point_set, point_list)

        shallow_in_triangle = sorted(point_list, key=lambda k: k.get_z())[0]
        shallow_z = sorted(z_vals, key=lambda k: k.get_z())[0]
        if shallow_in_triangle.get_z() < shallow_z.get_z():
            safety_violations.append(shallow_in_triangle)

    return safety_violations


def validate_legibility_constraint(generalized_soundings, generalized_tree, generalized_point_set, scale, h_spacing,
                                   v_spacing):
    legibility_violations = list()

    i = 0
    while i < len(generalized_soundings):
        target_sounding = generalized_soundings[i]
        search_window = get_character_dimensions(target_sounding, scale, h_spacing, v_spacing)[0]
        target_label = get_character_dimensions(target_sounding, scale, h_spacing, v_spacing)[1]
        point_list = list()

        generalized_tree.get_points_in_polygon(generalized_tree.get_root(), 0, generalized_point_set.get_domain(),
                                               search_window, generalized_point_set, point_list)

        for point in point_list:
            if point != target_sounding:
                point_label = get_character_dimensions(point, scale, h_spacing, v_spacing)[1]
                if target_label.intersects(point_label):
                    if target_sounding not in legibility_violations:
                        legibility_violations.append(target_sounding)
                    if point not in legibility_violations:
                        legibility_violations.append(point)

        i += 1

    return legibility_violations
