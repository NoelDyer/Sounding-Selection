from shapely.geometry import Polygon


class Writer(object):

    @staticmethod
    def write_soundings_file(file_name, vertices):
        out_url_xyz = file_name + ".txt"
        outfile_xyz = open(out_url_xyz, 'w')

        for v in vertices:
            outfile_xyz.write(v.__str__() + '\n')
        outfile_xyz.close()
        return

    @staticmethod
    def write_wkt_file(file_name, wkt):
        outfile_wkt = open(file_name, 'a+')
        outfile_wkt.write(str(wkt) + '\n')
        outfile_wkt.close()
        return

    @staticmethod
    def write_tin_file(tin, file_name):
        out_url = file_name + ".txt"
        outfile = open(out_url, 'w')

        for t_id in range(tin.get_triangles_num()):
            tri = tin.get_triangle(t_id)
            tri_points = list()
            for v in range(tri.get_vertices_num()):
                v_id = tri.get_tv(v)
                tri_points.append(tin.get_vertex(v_id))

            t = list()
            for point in tri_points:
                t.append([point.x_value, point.y_value])

            poly = Polygon(t)

            outfile.write(str(poly.wkt + '\n'))

        outfile.close()
        return
