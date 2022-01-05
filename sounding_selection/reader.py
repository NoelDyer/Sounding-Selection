import sys
import getopt
import csv
from vertex import Vertex
from pointset import PointSet
from tin import TIN
from triangles import Triangle
import shapely
from shapely import wkt
from shapely.ops import unary_union
from logger import log


class Reader(object):

    def read_arguments(self):
        input_file = None
        scale = None
        mqual = None
        horiz_spacing = 0.75
        vert_spacing = 0.75

        try:
            options, remainder = getopt.getopt(sys.argv[1:], "hi:s:m:x:y:")
        except getopt.GetoptError:
            print(sys.argv[0], ' -i <inputfile> -s <scale> -m <m_qual> -x <horizontal_spacing> -y <vertical_spacing>')
            sys.exit(2)
        for opt, arg in options:
            if opt == '-h':
                print(sys.argv[0], ' -i <inputfile> -s <scale> -m <m_qual> -x <horizontal_spacing>'
                                   ' -y <vertical_spacing>')
                sys.exit()
            elif opt in "-i":
                input_file = arg
            elif opt in "-s":
                scale = int(arg)
            elif opt in "-m":
                mqual = arg
            elif opt in "-x":
                horiz_spacing = float(arg)
            elif opt in "-y":
                vert_spacing = float(arg)

        if input_file is None:
            log.critical('Missing Source Sounding File')
            sys.exit()
        if scale is None:
            log.critical('Missing Scale')
            sys.exit()
        if mqual is None:
            log.warning('M_QUAL Not Provided')
        if horiz_spacing == 0.75:
            log.debug('Default Horizontal Character Spacing Set to 0.75 mm')
        else:
            log.debug('Horizontal Character Spacing Set to {} mm'.format(horiz_spacing))
        if vert_spacing == 0.75:
            log.debug('Default Vertical Character Spacing Set to {} mm'.format(vert_spacing))
        else:
            log.debug('Vertical Character Spacing Set to {} mm'.format(vert_spacing))

        return input_file, scale, mqual, horiz_spacing, vert_spacing

    def read_xyz_file(self, url_in):
        with open(url_in) as infile:
            point_set = PointSet()
            reader = csv.reader(infile, delimiter=',')
            for index, value in enumerate(reader):
                v = Vertex(float(value[0]), float(value[1]), float(value[2]))
                point_set.add_vertex(v)
                if index == 0:
                    point_set.set_domain(v, v)
                else:
                    point_set.get_domain().resize(v)
        infile.close()
        return point_set

    def read_wkt_file(self, url_in):
        wkt_file = open(url_in, 'r')
        wkt_string = wkt_file.read()
        wkt_file.close()

        wkt = shapely.wkt.loads(wkt_string)

        poly = unary_union(wkt)

        return poly

    def read_triangulation(self, triangulation, soundings_list):
        vertices = triangulation['vertices'].tolist()
        triangles = triangulation['triangles'].tolist()

        xy_list = [[float(v.get_x()), float(v.get_y())] for v in soundings_list]

        tin = TIN()
        for index, value in enumerate(vertices):
            if [float(value[0]), float(value[1])] in xy_list:
                index = xy_list.index([float(value[0]), float(value[1])])
                sounding = soundings_list[index]
                v = Vertex(float(sounding.get_x()), float(sounding.get_y()), float(sounding.get_z()))
            else:
                v = Vertex(float(value[0]), float(value[1]), float('NaN'))

            tin.add_vertex(v)
            if index == 0:
                tin.set_domain(v, v)
            else:
                tin.get_domain().resize(v)

        for tri in triangles:
            t = Triangle(int(tri[0]), int(tri[1]), int(tri[2]))
            tin.add_triangle(t)

        return tin
