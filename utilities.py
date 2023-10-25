import triangle
from sounding_selection.writer import Writer
from sounding_selection.vertex import Vertex
from shapely.geometry import shape, Point, Polygon
from shapely.ops import unary_union


def triangulate(sounding_vertex_list, segments=None, segments_idx=None, holes=None):
    """ Uses a Python wrapper of Triangle (Shechuck, 1996) to triangulate a set of points. Triangulation is
        constrained if bounding vertices are provided; otherwise the triangulation is Delaunay. """

    xy_list = [[v.x_value, v.y_value] for v in sounding_vertex_list]

    if segments is not None and segments_idx is not None and holes is not None:
        points = [[v.x_value, v.y_value] for v in segments]

        points.extend(xy_list)

        # Constrained
        if len(holes) > 0:
            triangulation = triangle.triangulate({'vertices': points,
                                                  'segments': segments_idx,
                                                  'holes': holes},
                                                  'pCSi')
        else:  # Assertion error is raised if empty list passed to triangulate
            triangulation = triangle.triangulate({'vertices': points,
                                                  'segments': segments_idx},
                                                  'pCSi')
        # p: PSLG; C: Exact arithmetic; S_: Steiner point limit; i: Incremental triangulation algorithm

    else:
        # Delaunay
        triangulation = triangle.triangulate({'vertices': xy_list})

    return triangulation


def get_feature_segments(depth_contours, depth_areas, boundary=True):
    """ Extracts contour and boundary segments and returns the coordinates as Vertex objects along with the associated
        index list."""

    geometry_dict = dict()
    geom_idx = 0
    depth_polygons, dredged_areas = list(), list()
    contour_depth_field = 'VALDCO'
    minimum_depth = 'DRVAL1'

    for shape_record in depth_areas.iterShapeRecords(fields=[minimum_depth, 'FCSubtype']):
        depth_area_geojson = shape_record.shape.__geo_interface__
        depth_area_polygon = shape(depth_area_geojson)
        if shape_record.record[1] == 5:
            controlling_depth = shape_record.record[0]
            dredged_areas.append([depth_area_polygon, controlling_depth])
        else:
            depth_polygons.append(depth_area_polygon)

    bathymetric_extent = unary_union(depth_polygons)
    dredged_extent = unary_union([dredged_area[0] for dredged_area in dredged_areas])

    if boundary is False:
        for contour_shape_record in depth_contours.iterShapeRecords(fields=[contour_depth_field]):
            if contour_shape_record.record[0] != 0:
                depth = contour_shape_record.record[0]
                contour_geojson = contour_shape_record.shape.__geo_interface__
                contour_linestring = shape(contour_geojson)
                contour_x, contour_y = contour_linestring.coords.xy
                geometry_dict[geom_idx] = list()
                for i in range(len(contour_x)):
                    geometry_dict[geom_idx].append(Vertex(contour_x[i], contour_y[i], depth))
                geom_idx += 1

    boundary_lines = list()
    if bathymetric_extent.geom_type == 'MultiPolygon':
        for polygon in bathymetric_extent.geoms:
            boundary = polygon.boundary
            if boundary.type == 'MultiLineString':
                for line in boundary.geoms:
                    boundary_lines.append(line)
            else:
                boundary_lines.append(boundary)

    elif bathymetric_extent.geom_type == 'Polygon':
        boundary = bathymetric_extent.boundary
        if boundary.type == 'MultiLineString':
            for line in boundary.geoms:
                boundary_lines.append(line)
        else:
            boundary_lines.append(boundary)

    for boundary_line in boundary_lines:
        line_x, line_y = boundary_line.coords.xy
        geometry_dict[geom_idx] = list()
        for i in range(len(line_x)):
            boundary_point, shoreline = True, False
            for contour_shape_record in depth_contours.iterShapeRecords(fields=[contour_depth_field]):
                if contour_shape_record.record[0] == 0:
                    contour_geojson = contour_shape_record.shape.__geo_interface__
                    contour_linestring = shape(contour_geojson)
                    if Point(line_x[i], line_y[i]).buffer(0.001).intersects(contour_linestring):
                        geometry_dict[geom_idx].append(Vertex(line_x[i], line_y[i], 0))
                        boundary_point, shoreline = False, True
                        break
            if shoreline is False:
                dredged_area_intersect = list()
                for dredged_area in dredged_areas:
                    if Point(line_x[i], line_y[i]).buffer(0.001).intersects(dredged_area[0]):
                        dredged_area_intersect.append(dredged_area[1])
                if len(dredged_area_intersect) > 0:
                    dredged_area_intersect.sort()
                    geometry_dict[geom_idx].append(Vertex(line_x[i], line_y[i], dredged_area_intersect[0]))
                    boundary_point = False

            if boundary_point is True:
                geometry_dict[geom_idx].append(Vertex(line_x[i], line_y[i], float(-99999)))
        geom_idx += 1

    segment_vertices, length_list = list(), list()
    for geom_idx in geometry_dict.keys():
        segment_length = len(geometry_dict[geom_idx])
        length_list.append(segment_length)
        for p in geometry_dict[geom_idx]:
            segment_vertices.append(p)

    Writer.write_soundings_file('boundary_points', segment_vertices)

    index_list = list()
    for i in range(len(length_list)):
        if i == 0:
            start = 0
            end = length_list[i]
        else:
            start = sum(length_list[:i])
            end = start + length_list[i]

        starting_point = segment_vertices[start]
        ending_point = segment_vertices[end-1]

        if starting_point == ending_point:
            index_list.extend(create_idx(start, end-1, closed=True))
        else:
            index_list.extend(create_idx(start, end-1, closed=False))

    holes = list()
    if bathymetric_extent.geom_type == 'Polygon':
        for interior in bathymetric_extent.interiors:
            hole_center = Polygon(interior).representative_point()
            holes.append([hole_center.x, hole_center.y])
    elif bathymetric_extent.geom_type == 'MultiPolygon':
        for part in bathymetric_extent.geoms:
            for interior in part.interiors:
                hole_center = Polygon(interior).representative_point()
                holes.append([hole_center.x, hole_center.y])

    return segment_vertices, index_list, holes, bathymetric_extent, dredged_extent


def create_idx(start, end, closed):
    """ Creates indexes for contour vertices so that segments can be created for a constrained triangulation. """

    if closed is True:
        return [[i, i + 1] for i in range(start, end)] + [[end, start]]
    else:
        return [[i, i + 1] for i in range(start, end)]


def modified_binary_search(sorted_vertices, vertex):
    """ Modified binary search algorithm to increase performance."""

    right, left = 0, 0
    vertices_num = len(sorted_vertices)

    while right < vertices_num:
        i = (right + vertices_num) // 2
        if vertex.z_value < sorted_vertices[i].z_value:
            vertices_num = i
        else:
            right = i + 1

    vertices_num = right - 1
    while left < vertices_num:
        i = (left + vertices_num) // 2
        if vertex.z_value > sorted_vertices[i].z_value:
            left = i + 1
        else:
            vertices_num = i

    if left == right-1:
        return left
    else:
        for idx in range(left, right):
            if sorted_vertices[idx] == vertex:
                return idx
