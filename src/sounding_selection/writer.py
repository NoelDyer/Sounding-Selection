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
        outfile_wkt = open(file_name, 'w')
        outfile_wkt.write(str(wkt) + '\n')
        outfile_wkt.close()
        return

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

