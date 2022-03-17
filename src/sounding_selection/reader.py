import sys
import getopt
import csv
import shapely
from shapely import wkt
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon
from sounding_selection.vertex import Vertex
from sounding_selection.pointset import PointSet
from sounding_selection.tin import TIN
from sounding_selection.triangles import Triangle
from sounding_selection.logger import log


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
            print(sys.argv[0], ' -i <inputfile> -s <scale> -m <m_qual> -x <horizontal_spacing>'
                               ' -y <vertical_spacing>')
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
        dissolve_wkt = unary_union(wkt)

        if dissolve_wkt.geom_type == 'MultiPolygon':
            poly = MultiPolygon(dissolve_wkt)
        elif dissolve_wkt.geom_type == 'Polygon':
            poly = Polygon(dissolve_wkt)
        else:
            log.critical('Provide Valid M_QUAL Polygon')
            sys.exit()

        return poly

    def read_triangulation(self, triangulation, vertex_list):
        vertices = triangulation['vertices']
        triangles = triangulation['triangles']

        xy_list = [[float(v.get_x()), float(v.get_y())] for v in vertex_list]

        tin = TIN()
        for i, v in enumerate(vertices):
            index = xy_list.index([float(v[0]), float(v[1])])
            sounding = vertex_list[index]
            vert = Vertex(float(sounding.get_x()), float(sounding.get_y()), float(sounding.get_z()))

            del xy_list[index]
            del vertex_list[index]

            tin.add_vertex(vert)
            if i == 0:
                tin.set_domain(vert, vert)
            else:
                tin.get_domain().resize(vert)

        for tri in triangles:
            t = Triangle(int(tri[0]), int(tri[1]), int(tri[2]))
            tin.add_triangle(t)

        return tin
