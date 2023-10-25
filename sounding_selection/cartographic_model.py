import math
from shapely.geometry import Polygon, Point
from shapely.affinity import scale as shapely_scale
from sounding_selection.logger import log

# FCSubtype legend:
# OBSTRN = 20
# UWTROC = 35
# WRECKS = 45


def get_carto_symbol(target_v, scale, horiz_spacing=None, vert_spacing=None):

    if target_v.s57_type is None:  # SOUNDG
        x_spacing = horiz_spacing / 2.0
        y_spacing = vert_spacing / 2.0

        n = abs(target_v.z_value)
        if n < 31:
            number = math.trunc(n * 10.0) / 10.0
            if number.is_integer():
                number = int(n)
        else:
            number = int(n)

        num_chars = len(str(number).replace('.', ''))
        is_decimal = False
        if '.' in str(number):
            is_decimal = True

        if num_chars == 1:  # 1 or 2
            x1 = -1.9 - x_spacing
            x2 = 0.025

        elif num_chars == 2:  # 22 or 2.2
            x1 = -1.9 - x_spacing
            if is_decimal is False:  # 22
                x2 = 1.9 + x_spacing
                x3 = None
                x4 = None
            else:
                x2 = 0.025
                if str(number).split('.')[1] == str(1):  # 2.1
                    x3 = 1.4 + x_spacing
                else:                                    # 2.2
                    x3 = 1.9 + x_spacing
                x4 = -0.025

        elif num_chars == 3:
            x1 = -4.15 - x_spacing
            if is_decimal is False:  # 222
                x2 = 1.9 + x_spacing
                x3 = None
                x4 = None
            else:                    # 11.1
                x2 = 0.025
                if str(number).split('.')[1] == str(1):
                    x3 = 1.4 + x_spacing
                else:
                    x3 = 1.9 + x_spacing
                x4 = -0.025

        y1, y2 = 1.4 + y_spacing, -1.4 - y_spacing

        if is_decimal is False:
            y3 = None
            y4 = None
        else:
            y3 = 0.15 + y_spacing
            y4 = -2.65 - y_spacing

        if is_decimal is False:
            p1 = target_v.x_value + mm_to_meters(x1, scale), target_v.y_value + mm_to_meters(y1, scale)
            p2 = target_v.x_value + mm_to_meters(x2, scale), target_v.y_value + mm_to_meters(y1, scale)
            p3 = target_v.x_value + mm_to_meters(x2, scale), target_v.y_value + mm_to_meters(y2, scale)
            p4 = target_v.x_value + mm_to_meters(x1, scale), target_v.y_value + mm_to_meters(y2, scale)

            label_polygon = Polygon([p1, p2, p3, p4])

        else:
            p1 = target_v.x_value + mm_to_meters(x1, scale), target_v.y_value + mm_to_meters(y1, scale)
            p2 = target_v.x_value + mm_to_meters(x2, scale), target_v.y_value + mm_to_meters(y1, scale)
            p3 = target_v.x_value + mm_to_meters(x2, scale), target_v.y_value + mm_to_meters(y3, scale)
            p4 = target_v.x_value + mm_to_meters(x3, scale), target_v.y_value + mm_to_meters(y3, scale)
            p5 = target_v.x_value + mm_to_meters(x3, scale), target_v.y_value + mm_to_meters(y4, scale)
            p6 = target_v.x_value + mm_to_meters(x4, scale), target_v.y_value + mm_to_meters(y4, scale)
            p7 = target_v.x_value + mm_to_meters(x4, scale), target_v.y_value + mm_to_meters(y2, scale)
            p8 = target_v.x_value + mm_to_meters(x1, scale), target_v.y_value + mm_to_meters(y2, scale)

            label_polygon = Polygon([p1, p2, p3, p4, p5, p6, p7, p8])

        if num_chars == 1:
            window_p1 = target_v.x_value + mm_to_meters(-4.57, scale), target_v.y_value + mm_to_meters(4.82, scale)
            window_p2 = target_v.x_value + mm_to_meters(4.57, scale), target_v.y_value + mm_to_meters(4.82, scale)
            window_p3 = target_v.x_value + mm_to_meters(4.57, scale), target_v.y_value + mm_to_meters(-3.57, scale)
            window_p4 = target_v.x_value + mm_to_meters(-4.57, scale), target_v.y_value + mm_to_meters(-3.57, scale)

            window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4])

        elif num_chars == 2 and is_decimal is True:
            if str(number).split('.')[1] == str(1):  # 0.1 2.1 A/E
                window_p1 = target_v.x_value + mm_to_meters(-5.32, scale), target_v.y_value + mm_to_meters(4.82, scale)
                window_p2 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(4.82, scale)
                window_p3 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(3.57, scale)
                window_p4 = target_v.x_value + mm_to_meters(4.82, scale), target_v.y_value + mm_to_meters(3.57, scale)
                window_p5 = target_v.x_value + mm_to_meters(4.82, scale), target_v.y_value + mm_to_meters(2.32, scale)
                window_p6 = target_v.x_value + mm_to_meters(7.07, scale), target_v.y_value + mm_to_meters(2.32, scale)
                window_p7 = target_v.x_value + mm_to_meters(7.07, scale), target_v.y_value + mm_to_meters(-4.82, scale)
                window_p8 = target_v.x_value + mm_to_meters(-3.07, scale), target_v.y_value + mm_to_meters(-4.82, scale)
                window_p9 = target_v.x_value + mm_to_meters(-3.07, scale), target_v.y_value + mm_to_meters(-3.57, scale)
                window_p10 = target_v.x_value + mm_to_meters(-5.32, scale), target_v.y_value + mm_to_meters(-3.57, scale)

                window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6, window_p7,
                                          window_p8, window_p9, window_p10])

            elif str(number).split('.')[1] != str(1):  # 0.5 1.0 2.0 B/F
                window_p1 = target_v.x_value + mm_to_meters(-5.32, scale), target_v.y_value + mm_to_meters(4.82, scale)
                window_p2 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(4.82, scale)
                window_p3 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(3.57, scale)
                window_p4 = target_v.x_value + mm_to_meters(5.32, scale), target_v.y_value + mm_to_meters(3.57, scale)
                window_p5 = target_v.x_value + mm_to_meters(5.32, scale), target_v.y_value + mm_to_meters(2.32, scale)
                window_p6 = target_v.x_value + mm_to_meters(7.57, scale), target_v.y_value + mm_to_meters(2.32, scale)
                window_p7 = target_v.x_value + mm_to_meters(7.57, scale), target_v.y_value + mm_to_meters(-4.82, scale)
                window_p8 = target_v.x_value + mm_to_meters(-3.07, scale), target_v.y_value + mm_to_meters(-4.82, scale)
                window_p9 = target_v.x_value + mm_to_meters(-3.07, scale), target_v.y_value + mm_to_meters(-3.57, scale)
                window_p10 = target_v.x_value + mm_to_meters(-5.32, scale), target_v.y_value + mm_to_meters(-3.57, scale)

                window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6, window_p7,
                                          window_p8, window_p9, window_p10])

        elif num_chars == 2 and is_decimal is False:  # 20 G
            window_p1 = target_v.x_value + mm_to_meters(-5.32, scale), target_v.y_value + mm_to_meters(4.82, scale)
            window_p2 = target_v.x_value + mm_to_meters(2.25, scale), target_v.y_value + mm_to_meters(4.82, scale)
            window_p3 = target_v.x_value + mm_to_meters(2.25, scale), target_v.y_value + mm_to_meters(3.57, scale)
            window_p4 = target_v.x_value + mm_to_meters(7.57, scale), target_v.y_value + mm_to_meters(3.57, scale)
            window_p5 = target_v.x_value + mm_to_meters(7.57, scale), target_v.y_value + mm_to_meters(-3.57, scale)
            window_p6 = target_v.x_value + mm_to_meters(-5.32, scale), target_v.y_value + mm_to_meters(-3.57, scale)

            window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6])

        elif num_chars == 3 and is_decimal is True:
            if str(number).split('.')[1] == str(1):  # 22.1 H
                window_p1 = target_v.x_value + mm_to_meters(-7.57, scale), target_v.y_value + mm_to_meters(4.82, scale)
                window_p2 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(4.82, scale)
                window_p3 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(3.57, scale)
                window_p4 = target_v.x_value + mm_to_meters(4.82, scale), target_v.y_value + mm_to_meters(3.57, scale)
                window_p5 = target_v.x_value + mm_to_meters(4.82, scale), target_v.y_value + mm_to_meters(2.32, scale)
                window_p6 = target_v.x_value + mm_to_meters(7.07, scale), target_v.y_value + mm_to_meters(2.32, scale)
                window_p7 = target_v.x_value + mm_to_meters(7.07, scale), target_v.y_value + mm_to_meters(-4.82, scale)
                window_p8 = target_v.x_value + mm_to_meters(-3.00, scale), target_v.y_value + mm_to_meters(-4.82, scale)
                window_p9 = target_v.x_value + mm_to_meters(-3.00, scale), target_v.y_value + mm_to_meters(-3.57, scale)
                window_p10 = target_v.x_value + mm_to_meters(-7.57, scale), target_v.y_value + mm_to_meters(-3.57, scale)

                window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6, window_p7,
                                          window_p8, window_p9, window_p10])

            elif str(number).split('.')[1] != str(1):  # 22.5 I
                window_p1 = target_v.x_value + mm_to_meters(-7.57, scale), target_v.y_value + mm_to_meters(4.82, scale)
                window_p2 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(4.82, scale)
                window_p3 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(3.57, scale)
                window_p4 = target_v.x_value + mm_to_meters(5.32, scale), target_v.y_value + mm_to_meters(3.57, scale)
                window_p5 = target_v.x_value + mm_to_meters(5.32, scale), target_v.y_value + mm_to_meters(2.32, scale)
                window_p6 = target_v.x_value + mm_to_meters(7.57, scale), target_v.y_value + mm_to_meters(2.32, scale)
                window_p7 = target_v.x_value + mm_to_meters(7.57, scale), target_v.y_value + mm_to_meters(-4.82, scale)
                window_p8 = target_v.x_value + mm_to_meters(-3.00, scale), target_v.y_value + mm_to_meters(-4.82, scale)
                window_p9 = target_v.x_value + mm_to_meters(-3.00, scale), target_v.y_value + mm_to_meters(-3.57, scale)
                window_p10 = target_v.x_value + mm_to_meters(-7.57, scale), target_v.y_value + mm_to_meters(-3.57, scale)

                window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6, window_p7,
                                          window_p8, window_p9, window_p10])

        elif num_chars == 3 and is_decimal is False:  # 200 J
            window_p1 = target_v.x_value + mm_to_meters(-7.57, scale), target_v.y_value + mm_to_meters(4.82, scale)
            window_p2 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(4.82, scale)
            window_p3 = target_v.x_value + mm_to_meters(0.82, scale), target_v.y_value + mm_to_meters(3.57, scale)
            window_p4 = target_v.x_value + mm_to_meters(7.57, scale), target_v.y_value + mm_to_meters(3.57, scale)
            window_p5 = target_v.x_value + mm_to_meters(7.57, scale), target_v.y_value + mm_to_meters(-3.57, scale)
            window_p6 = target_v.x_value + mm_to_meters(-7.57, scale), target_v.y_value + mm_to_meters(-3.57, scale)

            window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6])

        else:
            log.warning(str(number) + ': Depth Label Not Assigned')

        return window_polygon, label_polygon, number

    else:
        if target_v.z_value is not None and target_v.z_value > 0:  # Depth known
            if target_v.z_value < 20:  # S-52: DANGER01, DANGER03
                circle = Point(target_v.x_value, target_v.y_value).buffer(1)
                symbol = shapely_scale(circle, mm_to_meters(4.0, scale), mm_to_meters(3.16, scale))

            else:  # S-52: DANGER02
                circle = Point(target_v.x_value, target_v.y_value).buffer(1)
                symbol = shapely_scale(circle, mm_to_meters(4, scale), mm_to_meters(3.14, scale))

        else:  # Depth unknown or above water
            if target_v.s57_type == 45:  # WRECKS
                if target_v.s57_condition == 5:  # S-52: WRECKS01; exposed wreck
                    x1, y1 = target_v.x_value - mm_to_meters(3.5, scale), target_v.y_value - mm_to_meters(0.5, scale)
                    x2, y2 = target_v.x_value + mm_to_meters(3.0, scale), target_v.y_value - mm_to_meters(0.5, scale)
                    x3, y3 = target_v.x_value + mm_to_meters(0.6, scale), target_v.y_value + mm_to_meters(3.0, scale)
                    symbol = Polygon([Point(x1, y1), Point(x2, y2), Point(x3, y3)])

                elif target_v.s57_condition == 1:  # S-52: WRECKS04; non-dangerous wreck
                    circle = Point(target_v.x_value, target_v.y_value).buffer(1)
                    symbol = shapely_scale(circle, mm_to_meters(2.5, scale), mm_to_meters(1.5, scale))

                elif target_v.s57_condition == 2:  # S-52: WRECKS05; dangerous wreck
                    circle = Point(target_v.x_value, target_v.y_value).buffer(1)
                    symbol = shapely_scale(circle, mm_to_meters(2.95, scale), mm_to_meters(2.05, scale))

            elif target_v.s57_type == 35:  # UWTROC
                if target_v.s57_condition == 3:  # S-52: UWTROC03; submerged rock
                    symbol = Point(target_v.x_value, target_v.y_value).buffer(mm_to_meters(2.01, scale))
                else:  # S-52: UWTROC04; awash rock
                    circle = Point(target_v.x_value, target_v.y_value).buffer(1)
                    symbol = shapely_scale(circle, mm_to_meters(2.0, scale), mm_to_meters(1.625, scale))

            elif target_v.s57_type == 20:  # S-52: OBSTRN01, OBSTRN03; submerged/awash obstruction
                symbol = Point(target_v.x_value, target_v.y_value).buffer(mm_to_meters(2.05, scale))

        return symbol.buffer(mm_to_meters(3, scale)), symbol


def mm_to_meters(mm, scale):
    return (mm * float(scale)) / 1000
