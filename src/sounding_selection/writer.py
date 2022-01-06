import triangle
from shapely.geometry import Polygon


class Writer(object):

    def write_xyz_file(self, file_name, points):
        out_url_xyz = file_name + ".txt"
        outfile_xyz = open(out_url_xyz, 'w')

        for v in points:
            outfile_xyz.write(v.__str__() + '\n')
        outfile_xyz.close()
        return

    def write_wkt_file(self, file_name, wkt):
        outfile_wkt = open(file_name, 'a+')
        outfile_wkt.write(str(wkt) + '\n')
        outfile_wkt.close()
        return

    # Constrained Delaunay; Python wrapper of Triangle (Shechuck, 1996)
    def triangulate_xyz_constrained(self, xyz_list, mqual_wkt):
        soundings = [[v.get_x(), v.get_y(),  v.get_z()] for v in xyz_list]

        boundary_points, index_list = list(), list()
        if mqual_wkt.geom_type == 'MultiPolygon':
            for geom in mqual_wkt.geoms:
                x, y = geom.exterior.coords.xy
                for i in range(len(x)):
                    boundary_points.append([x[i], y[i], 'NaN'])

                if len(index_list) == 0:
                    for i in range(len(boundary_points) - 1):
                        index_list.append([i, i + 1])
                else:
                    for i in range(index_list[-1][1] + 1, len(boundary_points) - 1):
                        index_list.append([i, i + 1])
        elif mqual_wkt.geom_type == 'Polygon':
            x, y = mqual_wkt.exterior.coords.xy
            for i in range(len(x)):
                boundary_points.append([x[i], y[i], 'NaN'])

            for i in range(len(boundary_points) - 1):
                index_list.append([i, i + 1])

        boundary_points.extend(soundings)

        attributes = boundary_points[:]
        for point in attributes:
            point.append(0)

        all_points = [i[0:2] for i in boundary_points]

        triangulation = triangle.triangulate({'vertices': all_points,
                                              'segments': index_list,
                                              'regions': attributes},
                                              'pqiCDS0')

        return triangulation

    # Non-constrained Delaunay; Python wrapper of Triangle (Shechuck, 1996)
    def triangulate_xyz(self, xyz_list):
        xy_list = [[v.get_x(), v.get_y()] for v in xyz_list]
        
        triangulation = triangle.triangulate({'vertices': xy_list})

        return triangulation

    # output file format: WKT
    def write_tin_file(self, tin, file_name):
        out_url = file_name + ".txt"
        outfile = open(out_url, 'w')

        for t_id in range(tin.get_triangles_num()):
            tri = tin.get_triangle(t_id)
            tri_points = list()
            for v in range(tri.get_vertices_num()):
                v_id = tri.get_TV(v)
                tri_points.append(tin.get_vertex(v_id))

            t = list()
            for point in tri_points:
                t.append([point.get_x(), point.get_y()])

            poly = Polygon(t)

            outfile.write(str(poly.wkt + '\n'))

        outfile.close()
        return
