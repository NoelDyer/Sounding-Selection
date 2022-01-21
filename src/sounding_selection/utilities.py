import triangle
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union


def triangulate(vertex_list, boundary_vertices=None, boundary_indexes=None):
    """ Uses the Python wrapper of Triangle (Shechuck, 1996) to triangulate a set of points. Triangulation is
        constrained if bounding vertices are provided; otherwise the triangulation is Delaunay. """

    xy_list = [[v.get_x(), v.get_y()] for v in vertex_list]

    if boundary_vertices is not None and boundary_indexes is not None:
        boundary_points = [[v.get_x(), v.get_y()] for v in boundary_vertices]
        unique_points = [point for point in xy_list if point not in boundary_points]

        boundary_points.extend(unique_points)

        # Constrained
        triangulation = triangle.triangulate({'vertices': boundary_points,
                                              'segments': boundary_indexes},
                                              'pS0C')  # p: PSLG; S_: Steiner point limit; C: Exact arithmetic

    else:
        # Delaunay
        triangulation = triangle.triangulate({'vertices': xy_list})

    return triangulation


def fill_poly_gaps(mqual_poly):
    """ Fills gaps in MultiPolygons/Polygons by rebuilding the geometry from the exterior coordinates of each polygon
        and then using a bounding rectangle of the new polygons to eliminate any remaining gaps that can occur from
        touching polygon edges. Finally, removes co-linear vertices that can lead to precision issues during
        triangulation, which can cause boundary segments to be split. """

    parts = list()
    if mqual_poly.geom_type == 'MultiPolygon':
        for geom in mqual_poly.geoms:
            p = Polygon(geom.exterior.coords)
            parts.append(p)

        dissolve_poly = unary_union(parts)

        xmin, ymin, xmax, ymax = dissolve_poly.bounds
        bounding_rect = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]).buffer(1, resolution=1)

        geom_list = list()
        diff_poly = bounding_rect.difference(dissolve_poly)
        for diff_poly_geom in diff_poly.geoms:
            geom_list.append(diff_poly_geom)

        sorted_geoms = sorted(geom_list, key=lambda k: k.bounds)
        fill_poly = bounding_rect.difference(sorted_geoms[0])

        poly = fill_poly.buffer(0)

    else:
        p = mqual_poly.exterior.coords
        parts.append(p)

        dissolve_poly = unary_union(parts)
        xmin, ymin, xmax, ymax = dissolve_poly.bounds
        bounding_rect = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]).buffer(1, resolution=1)

        diff_poly = bounding_rect.difference(dissolve_poly)
        fill_poly = bounding_rect.difference(diff_poly)

        poly = fill_poly.buffer(0)

    if poly.geom_type == 'MultiPolygon':
        final_poly = MultiPolygon(poly.buffer(0))
    else:
        final_poly = Polygon(poly.buffer(0))

    return final_poly


def create_idx(start, end):
    """ Creates indexes for boundary vertices so that segments can be created for a constrained triangulation. """

    return [[i, i + 1] for i in range(start, end)] + [[end, start]]


def get_boundary_points(poly, point_set, point_tree):
    """ Extracts polygon vertex coordinates and returns the coordinates as Vertex objects along with the associated
        index list. """

    boundary_dict = dict()
    if poly.geom_type == 'MultiPolygon':
        for geom_index in range(len(poly.geoms)):
            boundary_dict[geom_index] = list()
            geom = poly.geoms[geom_index]
            x, y = geom.exterior.coords.xy
            for i in range(len(x) - 1):
                point_list = list()
                p = Point(x[i], y[i])
                p_buffer = p.buffer(0.00000001)

                point_tree.get_points_in_polygon(point_tree.get_root(), 0, point_set.get_domain(), p_buffer, point_set,
                                                 point_list)

                boundary_dict[geom_index].append(point_list[0])

    else:
        x, y = poly.exterior.coords.xy
        boundary_dict[0] = list()
        for i in range(len(x) - 1):
            point_list = list()
            p = Point(x[i], y[i])
            p_buffer = p.buffer(0.00000001)
            point_tree.get_points_in_polygon(point_tree.get_root(), 0, point_set.get_domain(), p_buffer, point_set,
                                             point_list)

            boundary_dict[0].append(point_list[0])

    boundary_vertices, length_list = list(), list()
    for poly_index in boundary_dict.keys():
        poly_length = len(boundary_dict[poly_index])
        length_list.append(poly_length-1)
        for vertex in boundary_dict[poly_index]:
            boundary_vertices.append(vertex)

    index_list = list()
    for i in range(len(length_list)):
        if i == 0:
            start = 0
            end = length_list[i]
        else:
            start = sum(length_list[:i]) + i
            end = start + length_list[i]
        index_list.extend(create_idx(start, end))

    return boundary_vertices, index_list


def simplify_mqual(triangulation, mqual_poly):
    """ Simplifies MQUAL boundary by taking an input Delaunay triangulation of the source soundings, and removing
        triangles whose centroid does not intersect the original MQUAL polygon. The simplified MQUAL boundary will have
        vertices that are in the source soundings dataset, which is important for the triangle test during validation.
        This process can result in geometries with unwanted gaps, which are eliminated using fill_poly_gaps(). """

    delete_triangles, tin_triangles,  = list(), list()
    # Get each triangle of the TIN
    for index, value in enumerate(triangulation['triangles']):
        tri_list = list()
        for v_id in value:
            tri_list.append(v_id)

        triangle_points = list()
        for vertex_id in tri_list:
            vertex = triangulation['vertices'][vertex_id]
            triangle_points.append([vertex[0], vertex[1]])

        triangle_poly = Polygon(triangle_points)
        tri_centroid = triangle_poly.centroid

        # Flag triangle if centroid is outside MQUAL polygon
        if mqual_poly.intersects(tri_centroid) is False:
            delete_triangles.append(triangle_poly)

        tin_triangles.append(triangle_poly)

    tin_shape = unary_union(tin_triangles)

    # Delete triangles from shape
    for delete_poly in delete_triangles:
        x, y = delete_poly.exterior.coords.xy
        delete_tri_points = list()
        for i in range(len(x) - 1):
            delete_tri_points.append(Point(x[i], y[i]))

        tin_shape = tin_shape.difference(delete_poly)

        # Check to ensure removed triangle does not exclude source soundings from simplified polygon
        intersect_check = [point.intersects(tin_shape) for point in delete_tri_points]
        if False in intersect_check:
            tin_shape.unary_union(delete_poly)

    if tin_shape.geom_type == 'MultiPolygon':
        simp_poly = MultiPolygon(tin_shape.buffer(0))
    else:
        simp_poly = Polygon(tin_shape.buffer(0))

    return simp_poly
