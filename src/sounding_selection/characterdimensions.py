import math
from shapely.geometry import Polygon
from sounding_selection.logger import log


def get_character_dimensions(target_v, scale, horiz_spacing, vert_spacing):
    x_spacing = horiz_spacing / 2.0
    y_spacing = vert_spacing / 2.0

    n = abs(target_v.get_z())
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
        p1 = target_v.get_x() + mm_to_meters(x1, scale), target_v.get_y() + mm_to_meters(y1, scale)
        p2 = target_v.get_x() + mm_to_meters(x2, scale), target_v.get_y() + mm_to_meters(y1, scale)
        p3 = target_v.get_x() + mm_to_meters(x2, scale), target_v.get_y() + mm_to_meters(y2, scale)
        p4 = target_v.get_x() + mm_to_meters(x1, scale), target_v.get_y() + mm_to_meters(y2, scale)

        label_polygon = Polygon([p1, p2, p3, p4])

    else:
        p1 = target_v.get_x() + mm_to_meters(x1, scale), target_v.get_y() + mm_to_meters(y1, scale)
        p2 = target_v.get_x() + mm_to_meters(x2, scale), target_v.get_y() + mm_to_meters(y1, scale)
        p3 = target_v.get_x() + mm_to_meters(x2, scale), target_v.get_y() + mm_to_meters(y3, scale)
        p4 = target_v.get_x() + mm_to_meters(x3, scale), target_v.get_y() + mm_to_meters(y3, scale)
        p5 = target_v.get_x() + mm_to_meters(x3, scale), target_v.get_y() + mm_to_meters(y4, scale)
        p6 = target_v.get_x() + mm_to_meters(x4, scale), target_v.get_y() + mm_to_meters(y4, scale)
        p7 = target_v.get_x() + mm_to_meters(x4, scale), target_v.get_y() + mm_to_meters(y2, scale)
        p8 = target_v.get_x() + mm_to_meters(x1, scale), target_v.get_y() + mm_to_meters(y2, scale)

        label_polygon = Polygon([p1, p2, p3, p4, p5, p6, p7, p8])

    if num_chars == 1:
        window_p1 = target_v.get_x() + mm_to_meters(-4.57, scale), target_v.get_y() + mm_to_meters(4.82, scale)
        window_p2 = target_v.get_x() + mm_to_meters(4.57, scale), target_v.get_y() + mm_to_meters(4.82, scale)
        window_p3 = target_v.get_x() + mm_to_meters(4.57, scale), target_v.get_y() + mm_to_meters(-3.57, scale)
        window_p4 = target_v.get_x() + mm_to_meters(-4.57, scale), target_v.get_y() + mm_to_meters(-3.57, scale)

        window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4])

    elif num_chars == 2 and is_decimal is True:
        if str(number).split('.')[1] == str(1):  # 0.1 2.1 A/E
            window_p1 = target_v.get_x() + mm_to_meters(-5.32, scale), target_v.get_y() + mm_to_meters(4.82, scale)
            window_p2 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(4.82, scale)
            window_p3 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(3.57, scale)
            window_p4 = target_v.get_x() + mm_to_meters(4.82, scale), target_v.get_y() + mm_to_meters(3.57, scale)
            window_p5 = target_v.get_x() + mm_to_meters(4.82, scale), target_v.get_y() + mm_to_meters(2.32, scale)
            window_p6 = target_v.get_x() + mm_to_meters(7.07, scale), target_v.get_y() + mm_to_meters(2.32, scale)
            window_p7 = target_v.get_x() + mm_to_meters(7.07, scale), target_v.get_y() + mm_to_meters(-4.82, scale)
            window_p8 = target_v.get_x() + mm_to_meters(-3.07, scale), target_v.get_y() + mm_to_meters(-4.82, scale)
            window_p9 = target_v.get_x() + mm_to_meters(-3.07, scale), target_v.get_y() + mm_to_meters(-3.57, scale)
            window_p10 = target_v.get_x() + mm_to_meters(-5.32, scale), target_v.get_y() + mm_to_meters(-3.57, scale)

            window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6, window_p7,
                                      window_p8, window_p9, window_p10])

        elif str(number).split('.')[1] != str(1):  # 0.5 1.0 2.0 B/F
            window_p1 = target_v.get_x() + mm_to_meters(-5.32, scale), target_v.get_y() + mm_to_meters(4.82, scale)
            window_p2 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(4.82, scale)
            window_p3 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(3.57, scale)
            window_p4 = target_v.get_x() + mm_to_meters(5.32, scale), target_v.get_y() + mm_to_meters(3.57, scale)
            window_p5 = target_v.get_x() + mm_to_meters(5.32, scale), target_v.get_y() + mm_to_meters(2.32, scale)
            window_p6 = target_v.get_x() + mm_to_meters(7.57, scale), target_v.get_y() + mm_to_meters(2.32, scale)
            window_p7 = target_v.get_x() + mm_to_meters(7.57, scale), target_v.get_y() + mm_to_meters(-4.82, scale)
            window_p8 = target_v.get_x() + mm_to_meters(-3.07, scale), target_v.get_y() + mm_to_meters(-4.82, scale)
            window_p9 = target_v.get_x() + mm_to_meters(-3.07, scale), target_v.get_y() + mm_to_meters(-3.57, scale)
            window_p10 = target_v.get_x() + mm_to_meters(-5.32, scale), target_v.get_y() + mm_to_meters(-3.57, scale)

            window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6, window_p7,
                                      window_p8, window_p9, window_p10])

    elif num_chars == 2 and is_decimal is False:  # 20 G
        window_p1 = target_v.get_x() + mm_to_meters(-5.32, scale), target_v.get_y() + mm_to_meters(4.82, scale)
        window_p2 = target_v.get_x() + mm_to_meters(2.25, scale), target_v.get_y() + mm_to_meters(4.82, scale)
        window_p3 = target_v.get_x() + mm_to_meters(2.25, scale), target_v.get_y() + mm_to_meters(3.57, scale)
        window_p4 = target_v.get_x() + mm_to_meters(7.57, scale), target_v.get_y() + mm_to_meters(3.57, scale)
        window_p5 = target_v.get_x() + mm_to_meters(7.57, scale), target_v.get_y() + mm_to_meters(-3.57, scale)
        window_p6 = target_v.get_x() + mm_to_meters(-5.32, scale), target_v.get_y() + mm_to_meters(-3.57, scale)

        window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6])

    elif num_chars == 3 and is_decimal is True:
        if str(number).split('.')[1] == str(1):  # 22.1 H
            window_p1 = target_v.get_x() + mm_to_meters(-7.57, scale), target_v.get_y() + mm_to_meters(4.82, scale)
            window_p2 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(4.82, scale)
            window_p3 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(3.57, scale)
            window_p4 = target_v.get_x() + mm_to_meters(4.82, scale), target_v.get_y() + mm_to_meters(3.57, scale)
            window_p5 = target_v.get_x() + mm_to_meters(4.82, scale), target_v.get_y() + mm_to_meters(2.32, scale)
            window_p6 = target_v.get_x() + mm_to_meters(7.07, scale), target_v.get_y() + mm_to_meters(2.32, scale)
            window_p7 = target_v.get_x() + mm_to_meters(7.07, scale), target_v.get_y() + mm_to_meters(-4.82, scale)
            window_p8 = target_v.get_x() + mm_to_meters(-3.00, scale), target_v.get_y() + mm_to_meters(-4.82, scale)
            window_p9 = target_v.get_x() + mm_to_meters(-3.00, scale), target_v.get_y() + mm_to_meters(-3.57, scale)
            window_p10 = target_v.get_x() + mm_to_meters(-7.57, scale), target_v.get_y() + mm_to_meters(-3.57, scale)

            window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6, window_p7,
                                      window_p8, window_p9, window_p10])

        elif str(number).split('.')[1] != str(1):  # 22.5 I
            window_p1 = target_v.get_x() + mm_to_meters(-7.57, scale), target_v.get_y() + mm_to_meters(4.82, scale)
            window_p2 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(4.82, scale)
            window_p3 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(3.57, scale)
            window_p4 = target_v.get_x() + mm_to_meters(5.32, scale), target_v.get_y() + mm_to_meters(3.57, scale)
            window_p5 = target_v.get_x() + mm_to_meters(5.32, scale), target_v.get_y() + mm_to_meters(2.32, scale)
            window_p6 = target_v.get_x() + mm_to_meters(7.57, scale), target_v.get_y() + mm_to_meters(2.32, scale)
            window_p7 = target_v.get_x() + mm_to_meters(7.57, scale), target_v.get_y() + mm_to_meters(-4.82, scale)
            window_p8 = target_v.get_x() + mm_to_meters(-3.00, scale), target_v.get_y() + mm_to_meters(-4.82, scale)
            window_p9 = target_v.get_x() + mm_to_meters(-3.00, scale), target_v.get_y() + mm_to_meters(-3.57, scale)
            window_p10 = target_v.get_x() + mm_to_meters(-7.57, scale), target_v.get_y() + mm_to_meters(-3.57, scale)

            window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6, window_p7,
                                      window_p8, window_p9, window_p10])

    elif num_chars == 3 and is_decimal is False:  # 200 J
        window_p1 = target_v.get_x() + mm_to_meters(-7.57, scale), target_v.get_y() + mm_to_meters(4.82, scale)
        window_p2 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(4.82, scale)
        window_p3 = target_v.get_x() + mm_to_meters(0.82, scale), target_v.get_y() + mm_to_meters(3.57, scale)
        window_p4 = target_v.get_x() + mm_to_meters(7.57, scale), target_v.get_y() + mm_to_meters(3.57, scale)
        window_p5 = target_v.get_x() + mm_to_meters(7.57, scale), target_v.get_y() + mm_to_meters(-3.57, scale)
        window_p6 = target_v.get_x() + mm_to_meters(-7.57, scale), target_v.get_y() + mm_to_meters(-3.57, scale)

        window_polygon = Polygon([window_p1, window_p2, window_p3, window_p4, window_p5, window_p6])

    else:
        log.warning(str(number) + ': Depth Label Not Assigned')

    return window_polygon, label_polygon, number


def mm_to_meters(mm, scale):
    return (mm * float(scale)) / 1000
