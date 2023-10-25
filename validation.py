from shapely.geometry import Polygon, Point, shape
from sounding_selection.logger import log
from sounding_selection.catzoc import *
from sounding_selection.cartographic_model import get_carto_symbol


def validate_functionality_constraint(generalized_tin, validation_tree, validation_point_set, depth_areas,
                                      method='TRIANGLE'):

    safety_violations = list()
    if method == 'TRIANGLE':
        for t_id in range(generalized_tin.get_triangles_num()):
            tri = generalized_tin.get_triangle(t_id)
            tri_points = list()
            for v in range(tri.get_vertices_num()):
                v_id = tri.get_tv(v)
                tri_points.append(generalized_tin.get_vertex(v_id))

            z_vals, triangle = list(), list()
            for point in tri_points:
                z_vals.append(point.z_value)
                triangle.append([point.x_value, point.y_value])

            if float(-99999) not in z_vals:
                in_triangle_list = list()
                validation_tree.points_in_polygon(validation_tree.get_root(), 0, validation_point_set.get_domain(),
                                                  Polygon(triangle), validation_point_set, in_triangle_list)

                if len(in_triangle_list) > 0:
                    shallow_in_triangle = sorted(in_triangle_list, key=lambda k: k.z_value)[0]
                    shallow_z = sorted(z_vals)[0]
                    if shallow_in_triangle.z_value < shallow_z:
                        if all(z == z_vals[0] for z in z_vals):
                            for shape_record in depth_areas.iterShapeRecords(fields=['DRVAL1']):
                                depth_area_geojson = shape_record.shape.__geo_interface__
                                depth_polygon = shape(depth_area_geojson)
                                shallow_in_tri_point = Point(shallow_in_triangle.x_value, shallow_in_triangle.y_value)
                                if shallow_in_tri_point.intersects(depth_polygon):
                                    drval1 = shape_record.record[0]
                                    if shallow_in_triangle.z_value < drval1:
                                        safety_violations.append(shallow_in_triangle)
                                    break

                        else:
                            safety_violations.append(shallow_in_triangle)

    elif method == 'SURFACE':
        catzoc_dict = {1: 'A1',
                       2: 'A2',
                       3: 'B',
                       4: 'C',
                       5: 'D',
                       6: 'U'}

        for t_id in range(generalized_tin.get_triangles_num()):
            tri = generalized_tin.get_triangle(t_id)
            tri_points = list()
            for v in range(tri.get_vertices_num()):
                v_id = tri.get_tv(v)
                tri_points.append(generalized_tin.get_vertex(v_id))

            triangle, z_vals, catzoc_values = list(), list(), list()
            for point in tri_points:
                z_vals.append(point.z_value)
                triangle.append([point.x_value, point.y_value])
                catzoc_values.append(point.catzoc_value)

            # Use the highest quality catzoc of the triangle
            catzoc_sorted = sorted([c for c in catzoc_values if c is not None])
            if len(catzoc_sorted) > 0:
                best_catzoc = catzoc_sorted[0]
                catzoc = catzoc_dict[best_catzoc]
            else:
                catzoc = catzoc_dict[6]

            # Skip triangles along boundary; cannot assess triangles with no depth tolerance (D and U)
            if float(-99999) not in z_vals and catzoc != 'U' and catzoc != 'D':
                intersect_triangle_list = list()
                validation_tree.points_in_polygon(validation_tree.get_root(), 0, validation_point_set.get_domain(),
                                                  Polygon(triangle), validation_point_set, intersect_triangle_list)

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

                    # if abs(interp_z - actual_z) > depth_tolerance(catzoc, actual_z):  # Shallow and deep violations
                    if interp_z - actual_z > depth_tolerance(catzoc, actual_z):  # Shallow violations
                        difference_list.append([v, interp_z - actual_z])

                # Identify soundings with largest difference
                if len(difference_list) > 0:
                    diff_sorted = sorted(difference_list, key=lambda k: k[1], reverse=True)
                    largest_violation = diff_sorted[0][0]
                    if largest_violation not in safety_violations:  # Triangle can be indexed to multiple nodes
                        safety_violations.append(largest_violation)

    else:
        log.info('Functionality Validation Method Not Provided')

    return safety_violations


def validate_legibility_constraint(soundings, soundings_tree, soundings_point_set, scale, h_spacing, v_spacing):

    legibility_violations = list()

    i = 0
    while i < len(soundings):
        target_sounding = soundings[i]
        search_window = get_carto_symbol(target_sounding, scale, h_spacing, v_spacing)[0]
        target_label = get_carto_symbol(target_sounding, scale, h_spacing, v_spacing)[1]
        point_list = list()

        soundings_tree.points_in_polygon(soundings_tree.get_root(), 0, soundings_point_set.get_domain(), search_window,
                                         soundings_point_set, point_list)

        for point in point_list:
            if point != target_sounding:
                point_label = get_carto_symbol(point, scale, h_spacing, v_spacing)[1]
                if target_label.intersects(point_label):
                    if target_sounding not in legibility_violations:
                        legibility_violations.append(target_sounding)
                    if point not in legibility_violations:
                        legibility_violations.append(point)

        i += 1

    return legibility_violations


def check_vertex_legibility(vertex, selection_tree, selection_point_set, scale, h_spacing, v_spacing):
    legibility_violations = list()

    search_window = get_carto_symbol(vertex, scale, h_spacing, v_spacing)[0]
    target_label = get_carto_symbol(vertex, scale, h_spacing, v_spacing)[1]

    potential_violations = list()
    selection_tree.points_in_polygon(selection_tree.get_root(), 0, selection_point_set.get_domain(), search_window,
                                     selection_point_set, potential_violations)

    for potential_violation in potential_violations:
        if potential_violation != vertex:
            potential_violation_label = get_carto_symbol(potential_violation, scale, h_spacing, v_spacing)[1]
            if target_label.intersects(potential_violation_label):
                legibility_violations.append(potential_violation)

    return legibility_violations
