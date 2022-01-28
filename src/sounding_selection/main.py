import datetime
from sounding_selection.utilities import *
from sounding_selection.reader import Reader
from sounding_selection.writer import Writer
from sounding_selection.tree import Tree
from sounding_selection.validation import *
from sounding_selection.logger import log
from shapely.geometry import Point
from timeit import default_timer as timer


def main():
    # Initialize Reader/Writer class
    reader = Reader()
    writer = Writer()

    # Read input arguments
    source_soundings, scale, mqual, horiz_spacing, vert_spacing = reader.read_arguments()

    # Read x,y,z file into point set
    log.info('-Reading Source Soundings File')
    source_point_set = reader.read_xyz_file(source_soundings)

    # Initialize Tree class
    log.info('-Building PR-Quadtree')
    capacity = int(source_point_set.get_vertices_num() * 0.0004)
    source_tree = Tree(int(capacity))
    validation_source_tree = Tree(int(capacity))  # used later for validation

    # Build PR-quadtree of source points
    source_tree.build_point_tree(source_point_set)
    validation_source_tree.build_point_tree(source_point_set)  # used later for validation

    # Read M_QUAL into polygon object and simplify; store boundary points for triangulation process during validation
    if mqual is not None:
        log.info('-Processing M_QUAL File')
        mqual_wkt = reader.read_wkt_file(mqual)

        log.info('\t-Simplifying M_QUAL Boundary')
        source_tri = triangulate(source_point_set.get_all_vertices())
        simplified_mqual = simplify_mqual(source_tri, mqual_wkt)
        # writer.write_wkt_file('Simplified_MQUAL.txt', simplified_mqual)

        log.info('\t-Removing Polygon Holes')
        m_qual_poly = fill_poly_gaps(simplified_mqual)
        # writer.write_wkt_file('Gap_Filled_MQUAL.txt', m_qual_poly)

        log.info('\t-Extracting Boundary Points')
        boundary_vertices, boundary_idx = get_boundary_points(m_qual_poly, source_point_set, source_tree)
        writer.write_xyz_file('MQUAL_Boundary_Points', boundary_vertices)

    else:
        boundary_vertices = None
        boundary_idx = None

    # Create list to store generalized soundings
    generalized_soundings = list()

    # Sorted list of the point set sorted from low to high
    sorted_points = sorted(source_point_set.get_all_vertices(), key=lambda k: k.get_z())

    # Generalization and timing
    start = timer()
    log.info('-Processing Label-Based Generalization')
    # Iterate through sorted point set
    while len(sorted_points) > 0:
        deletes = list()
        source_tree.generalize(source_tree.get_root(), 0, source_point_set.get_domain(), sorted_points[0],
                               source_point_set, deletes, scale, horiz_spacing, vert_spacing)
        # Delete generalized soundings from sorted points list
        for i in deletes:
            delete_idx = modified_binary_search(sorted_points, i)
            del sorted_points[delete_idx]
        generalized_soundings.append(sorted_points[0])
        del sorted_points[0]

    end = timer()

    # Report timing of generalization
    time_elapsed = end - start
    hours = str(datetime.timedelta(seconds=time_elapsed)).split(':')[0]
    minutes = str(datetime.timedelta(seconds=time_elapsed)).split(':')[1]
    seconds = str(datetime.timedelta(seconds=time_elapsed)).split(':')[2]
    if float(hours) > 0:
        log.info('\t--Generalization Time: ' + hours + ' hours, ' + minutes + ' minutes, ' + str(seconds) + ' seconds')
    else:
        log.info('\t--Generalization Time: ' + minutes + ' minutes, ' + str(int(float(seconds))) + ' seconds')

    # Evaluate output against cartographic constraints
    log.info('-Evaluating Cartographic Constraint Violations')

    # Triangulate generalized soundings
    tri = triangulate(generalized_soundings, boundary_vertices, boundary_idx)

    # Read tin into class
    if boundary_vertices is not None:
        combined = generalized_soundings + boundary_vertices
    else:
        combined = generalized_soundings
    generalized_tin = reader.read_triangulation(tri, combined)
    out_name = str(source_soundings).split('.')[0] + '_Generalized'
    writer.write_tin_file(generalized_tin, out_name + '_Initial_TIN')

    # First evaluation of functionality (safety) constraint
    functionality_violations = validate_functionality_constraint(generalized_tin, validation_source_tree,
                                                                 source_point_set, scale, horiz_spacing, vert_spacing)

    # First evaluation of legibility constraint
    legibility_violations = validate_legibility_constraint(generalized_soundings, source_tree, source_point_set, scale,
                                                           horiz_spacing, vert_spacing)

    # Adjust for functionality (safety) violations
    if len(functionality_violations) == 0:
        log.info('\t--Safety Constraint Violations: ' + str(len(functionality_violations)))
        log.info('\t--Legibility Violations: ' + str(len(set(legibility_violations))))

        # Write generalized soundings
        log.info('-Writing Generalized Soundings File')
        writer.write_xyz_file(out_name, generalized_soundings)
    else:
        log.info('\t--Initial Generalized Soundings Count: ' + str(len(generalized_soundings)))
        log.info('\t--Initial Functionality (Safety) Constraint Violations: ' + str(len(functionality_violations)))
        log.info('\t--Initial Legibility Violations: ' + str(len(legibility_violations)))
        log.info('-Adjusting Selection for Functionality (Safety) Constraint Violations')

        iteration_count, i = 0, 0
        while len(functionality_violations) > 0:
            # Adjust for violations inside generalized sounding labels
            while i < len(generalized_soundings):
                target_sounding = generalized_soundings[i]
                target_label = get_character_dimensions(target_sounding, scale, horiz_spacing, vert_spacing)[1]
                violation_in_label = list()
                for func_violation in functionality_violations:
                    violation_point = Point(func_violation.get_x(), func_violation.get_y())
                    if violation_point.intersects(target_label):
                        violation_in_label.append(func_violation)
                if len(violation_in_label) > 0:
                    shallow_violation = sorted(violation_in_label, key=lambda k: k.get_z())[0]
                    target_sounding.set_x(shallow_violation.get_x())
                    target_sounding.set_y(shallow_violation.get_y())
                    target_sounding.set_z(shallow_violation.get_z())
                for violation in violation_in_label:
                    functionality_violations.remove(violation)

                i += 1

            # Combine adjusted generalized soundings with remaining violations
            for violation in functionality_violations:
                if violation not in generalized_soundings:
                    generalized_soundings.append(violation)

            # Re-triangulate updated generalized soundings
            boundary_pointset = reader.read_xyz_file('MQUAL_Boundary_Points.txt')
            boundary_vertices = boundary_pointset.get_all_vertices()
            tri = triangulate(generalized_soundings, boundary_vertices, boundary_idx)

            # Iteration of functionality (safety) constraint evaluation
            if boundary_vertices is not None:
                combined = generalized_soundings + boundary_vertices
            else:
                combined = generalized_soundings
            generalized_tin = reader.read_triangulation(tri, combined)
            functionality_violations = validate_functionality_constraint(generalized_tin, validation_source_tree,
                                                                         source_point_set, scale, horiz_spacing,
                                                                         vert_spacing)

            iteration_count += 1
            log.info('\t--Iteration Count: ' + str(iteration_count))
            log.info('\t\t--Violations: ' + str(len(functionality_violations)))

        # Evaluate adjusted legibility constraint
        legibility_violations = validate_legibility_constraint(generalized_soundings, source_tree, source_point_set,
                                                               scale, horiz_spacing, vert_spacing)

        log.info('\t\t--Final Generalized Soundings Count: ' + str(len(generalized_soundings)))
        log.info('\t\t--Final Iteration Adjusted Functionality (Safety) Violations: ' + str(len(functionality_violations)))
        log.info('\t\t--Final Iteration Adjusted Legibility Violations: ' + str(len(legibility_violations)))

        # Write adjusted generalized soundings
        log.info('-Writing Adjusted Generalized Soundings File')
        writer.write_xyz_file(out_name, generalized_soundings)

    # Write label dimension files
    log.info('-Writing Label Polygon Files')
    for vertex in generalized_soundings:
        target_label = get_character_dimensions(vertex, scale, horiz_spacing, vert_spacing)[1]
        writer.write_wkt_file(out_name + r'_label_wkt.txt', target_label)
        # window = get_character_dimensions(vertex, scale, horiz_spacing, vert_spacing)[0]
        # writer.write_wkt_file(out_name + r'_window_wkt.txt', window.wkt)

    # Write legibility violations, reports violating sounding
    log.info('-Writing Constraint Violation Files')
    if len(legibility_violations) > 0:
        writer.write_xyz_file(str(source_soundings).split('.')[0] + '_Generalized_Legibility_violations',
                              legibility_violations)

    # No functionality violations should be reported due to adjustment procedure
    if len(functionality_violations) > 0:
        writer.write_xyz_file(str(source_soundings).split('.')[0] + '_Generalized_Safety_Violations',
                              functionality_violations)

    writer.write_tin_file(generalized_tin, out_name + '_Final_TIN')

    log.info('-Hydrographic Sounding Selection Complete')

    return


if __name__ == '__main__':
    main()
