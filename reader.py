import sys
import getopt
import csv
import shapely
from shapely import wkt
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon, shape
from sounding_selection.vertex import Vertex
from sounding_selection.pointset import PointSet
from sounding_selection.tin import TIN
from sounding_selection.triangles import Triangle
from sounding_selection.logger import log


class Reader(object):

    @staticmethod
    def read_arguments():
        input_file = None
        scale = None
        validation = None
        enc_soundings = None
        depth_areas = None
        dangers = None
        depth_contours = None
        starting_radius = None
        ending_radius = None
        horiz_spacing = 0.75
        vert_spacing = 0.75

        try:
            options, remainder = getopt.getopt(sys.argv[1:], "hi:r:v:c:a:d:n:s:e:x:y:")
        except getopt.GetoptError:
            print(sys.argv[0], ' -i <inputfile> -r <scale> -v <validation> -c <chart_soundings> -a <depth_areas>'
                               ' -d <depth_contours> -n <dangers_to_navigation> -s <starting_radius_length>'
                               ' -e <ending_radius_length> -x <horizontal_spacing> -y <vertical_spacing>')
            sys.exit(2)
        for opt, arg in options:
            if opt == '-h':
                print(sys.argv[0], ' -i <inputfile> -r <scale> -v <validation> -c <chart_soundings> -a <depth_areas>'
                                   ' -d <depth_contours> -s <starting_radius_length> -e <ending_radius_length>'
                                   ' -x <horizontal_spacing> -y <vertical_spacing>')
                sys.exit()
            elif opt in "-i":
                input_file = str(arg)
            elif opt in "-r":
                scale = int(arg)
            elif opt in "-v":
                validation = str(arg).upper()
            elif opt in "-c":
                enc_soundings = str(arg)
            elif opt in "-a":
                depth_areas = str(arg)
            elif opt in "-d":
                depth_contours = str(arg)
            elif opt in "-n":
                dangers = str(arg)
            elif opt in "-s":
                starting_radius = float(arg)
            elif opt in "-e":
                ending_radius = float(arg)
            elif opt in "-x":
                horiz_spacing = float(arg)
            elif opt in "-y":
                vert_spacing = float(arg)

        if input_file is None:
            log.critical('Source Sounding File Not Provided')
            sys.exit()
        if scale is None:
            log.critical('Scale Not Provided')
            sys.exit()
        if scale not in [10000, 15000, 20000, 25000, 40000, 80000, 160000, 320000, 640000, 1280000, 2560000, 5120000]:
            log.critical('Select Scale from: 10000, 20000, 25000, 40000, 80000, 160000, 320000, 640000, 1280000, '
                         '2560000, 5120000')
            sys.exit()
        if enc_soundings is None:
            log.critical('Chart Soundings Not Provided')
            sys.exit()
        if depth_areas is None:
            log.critical('Depth Areas Not Provided')
            sys.exit()
        if depth_contours is None:
            log.critical('Depth Contours Not Provided')
            sys.exit()
        if dangers is None:
            log.warning('Dangers to Navigation Not Provided')
        if starting_radius is None:
            log.critical('Starting Radius Length Not Provided')
            sys.exit()
        if ending_radius is None:
            log.critical('Ending Radius Length Not Provided')
            sys.exit()
        if validation is None:
            log.critical('Functionality Constraint Validation Method Not Provided')
            sys.exit()
        if validation is not None and validation not in ['TRIANGLE', 'SURFACE']:
            log.critical('Provide Valid Functionality Constraint Validation Method: TRIANGLE or SURFACE')
            sys.exit()

        return input_file, scale, validation, enc_soundings, depth_areas, depth_contours, dangers, starting_radius, \
            ending_radius, horiz_spacing, vert_spacing

    @staticmethod
    def read_xyz_to_pointset(url_in):
        with open(url_in) as infile:
            point_set = PointSet()
            reader = csv.reader(infile, delimiter=',')
            for index, value in enumerate(reader):
                if float(value[2]) < 0:
                    v = Vertex(x=float(value[0]), y=float(value[1]), z=abs(float(value[2])), catzoc=float(value[3]))
                    point_set.add_vertex(v)
                    if index == 0:
                        point_set.set_domain(v, v)
                    else:
                        point_set.get_domain().resize(v)
        infile.close()
        return point_set

    @staticmethod
    def read_vertex_list_to_pointset(vertex_list):
        point_set = PointSet()
        for index, vertex in enumerate(vertex_list):
            point_set.add_vertex(vertex)
            if index == 0:
                point_set.set_domain(vertex, vertex)
            else:
                point_set.get_domain().resize(vertex)
        return point_set

    @staticmethod
    def read_xyz_to_vertex_list(url_in):
        vertex_list = list()
        with open(url_in) as infile:
            reader = csv.reader(infile, delimiter=',')
            for point in reader:
                if float(point[2]) < 0:
                    v = Vertex(x=float(point[0]), y=float(point[1]), z=abs(float(point[2])), catzoc=float(point[3]))
                    vertex_list.append(v)
        infile.close()
        return vertex_list

    @staticmethod
    def read_dtons_to_vertex_list(dangers_p):
        vertex_list = list()
        for shape_record in dangers_p.iterShapeRecords(fields=['VALSOU', 'WATLEV', 'FCSUBTYPE', 'CATWRK']):
            s57_subtype = shape_record.record[2]
            if s57_subtype == 35 or s57_subtype == 20 or s57_subtype == 45:
                danger_geojson = shape_record.shape.__geo_interface__
                danger_point = shape(danger_geojson)
                x, y = danger_point.x, danger_point.y

                if shape_record.record[0] == -32767:  # Null value
                    z = None
                elif shape_record.record[0] < 0:
                    z = 0.0
                else:
                    z = float(shape_record.record[0])

                if s57_subtype == 35 or s57_subtype == 20:
                    s57_condtn = shape_record.record[1]
                else:
                    s57_condtn = shape_record.record[3]

                v = Vertex(x=float(x), y=float(y), z=z, s57_type=float(s57_subtype), s57_condition=float(s57_condtn))
                vertex_list.append(v)

        return vertex_list

    @staticmethod
    def read_wkt_file(url_in):
        wkt_file = open(url_in, 'r')
        wkt_string = wkt_file.read()
        wkt_file.close()

        wkt = shapely.wkt.loads(wkt_string)
        dissolve_wkt = unary_union(wkt)

        if dissolve_wkt.geom_type == 'MultiPolygon':
            poly = MultiPolygon(dissolve_wkt)
        elif dissolve_wkt.geom_type == 'Polygon':
            poly = Polygon(dissolve_wkt)
        else:
            log.critical('Provide Valid M_QUAL Polygon')
            sys.exit()

        return poly

    @staticmethod
    def read_triangulation(triangulation, vertex_list):
        vertices = triangulation['vertices']
        triangles = triangulation['triangles']

        v_list = vertex_list[:]
        xy_list = [[float(v.x_value), float(v.y_value)] for v in v_list]

        tin = TIN()
        for i, v in enumerate(vertices):
            index = xy_list.index([float(v[0]), float(v[1])])
            sounding_vertex = v_list[index]

            del xy_list[index]
            del v_list[index]

            tin.add_vertex(sounding_vertex)
            if i == 0:
                tin.set_domain(sounding_vertex, sounding_vertex)
            else:
                tin.get_domain().resize(sounding_vertex)

        for tri in triangles:
            t = Triangle(int(tri[0]), int(tri[1]), int(tri[2]))
            tin.add_triangle(t)

        return tin
