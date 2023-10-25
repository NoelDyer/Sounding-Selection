import shapefile
from math import ceil
from sounding_selection.utilities import *
from sounding_selection.reader import Reader
from sounding_selection.writer import Writer
from sounding_selection.tree import Tree
from sounding_selection.validation import *
from sounding_selection.logger import log
from shapely.geometry import shape, Polygon, Point


def main():

    # Read input arguments
    source, scale, validation_method, existing_soundings, depth_areas, depth_contours, danger_points, starting_radius, \
        ending_radius, horiz_spacing, vert_spacing = Reader.read_arguments()

########################################################################################################################

    # Source bathymetry (ENC/input survey) surface model analysis
    log.info('-Generating Bathymetric Surface Model')

    # Read input depth areas and extract boundary to constrain the triangulation of source and existing ENC soundings
    log.info('\t--Reading Bathymetric Extent and Depth Contours')
    depth_polygons = shapefile.Reader(depth_areas)
    contours = shapefile.Reader(depth_contours)
    boundary_segment_vertices, boundary_idx_list, holes, bathy_extent, dredged_extent = get_feature_segments(contours, depth_polygons)

    Writer.write_wkt_file('bathymetric_extent.txt', bathy_extent)

    # Read source sounding x,y,z file into vertex list
    log.info('\t--Reading Source Soundings File')
    source_all = Reader.read_xyz_to_vertex_list(source)
    source_soundings = [v for v in source_all if Point(v.x_value, v.y_value).intersects(bathy_extent) is True]
    source_pointset = Reader.read_vertex_list_to_pointset(source_soundings)
    Writer.write_soundings_file('source_soundings', source_soundings)

    # Read chart sounding x,y,z file into vertex list and PR-Quadtree
    log.info('\t--Reading Chart Soundings File')
    chart_soundings_pointset = Reader.read_xyz_to_pointset(existing_soundings)
    chart_soundings = [v for v in chart_soundings_pointset.get_all_vertices() if Point(v.x_value, v.y_value).intersects(bathy_extent) is True]

    log.info('\t\t--Building PR-Quadtree for Chart Soundings')
    chart_soundings_capacity = int(ceil(len(chart_soundings) * 0.004))
    chart_soundings_tree = Tree(chart_soundings_capacity)
    chart_soundings_tree.build_point_tree(chart_soundings_pointset)

    # Read dangers to navigation point file into vertex list
    log.info('\t--Reading Dangers to Navigation File')
    dangers_p = shapefile.Reader(danger_points)
    dangers = Reader.read_dtons_to_vertex_list(dangers_p)
    dangers_with_depth = [danger for danger in dangers if danger.z_value is not None and Point(danger.x_value, danger.y_value).intersects(bathy_extent) is True]
    for d in dangers:
        target_label = get_carto_symbol(d, scale)[1]
        Writer.write_wkt_file('DTON_DCM_WKT.txt', target_label.wkt)

    # Triangulate and build TIN tree
    log.info('\t--Triangulating Danger to Navigation Points, Source Soundings, and Existing ENC Soundings')
    source_chart_dangers = source_soundings + chart_soundings + dangers_with_depth
    source_chart_dangers_boundary = source_chart_dangers + boundary_segment_vertices
    source_chart_dangers_tri = triangulate(source_chart_dangers, boundary_segment_vertices, boundary_idx_list, holes)
    source_chart_dangers_tin = Reader.read_triangulation(source_chart_dangers_tri, source_chart_dangers_boundary)

    log.info('\t\t--Building TIN PR-Quadtree')
    source_chart_dangers_capacity = int(ceil(len(source_chart_dangers) * 0.004))
    source_chart_dangers_tin_tree = Tree(source_chart_dangers_capacity)
    source_chart_dangers_tin_tree.build_tin_tree(source_chart_dangers_tin)

    # Write output TIN
    log.info('\t\t--Writing Danger to Navigation Points, Source Soundings, and Existing ENC Sounding TIN File')
    Writer.write_tin_file(source_chart_dangers_tin, 'Bathymetric_Surface_Model_TIN')

    log.info('\t--Analyzing Characteristics of Bathymetric Surface Model')
    # Identify shoal, supporting, and deep soundings (critical points) from input (source) bathymetry
    log.info('\t\t--Identifying Critical Points')

    # Extract critical points of combined source and existing sounding triangulation
    source_chart_dangers_tin_tree.crit_query(source_chart_dangers_tin_tree.get_root(), 0,
                                             source_chart_dangers_tin.get_domain(), source_chart_dangers_tin)

    # Report counts of shoal, supporting, and deep soundings
    source_surface_model_maxima = [v for v in source_chart_dangers if v.sounding_type is 'Maxima']
    source_surface_model_saddle = [v for v in source_chart_dangers if v.sounding_type is 'Saddle']
    source_surface_model_minima = [v for v in source_chart_dangers if v.sounding_type is 'Minima']
    log.info('\t\t\t--Bathymetric Surface Model Maxima Count: ' + str(len(source_surface_model_maxima)))
    log.info('\t\t\t--Bathymetric Surface Model Saddle Count: ' + str(len(source_surface_model_saddle)))
    log.info('\t\t\t--Bathymetric Surface Model Minima Count: ' + str(len(source_surface_model_minima)))

    # Write output files
    log.info('\t\t--Writing Critical Point Output Files')
    Writer.write_soundings_file('Bathymetric_Surface_Model_Maximas', source_surface_model_maxima)
    Writer.write_soundings_file('Bathymetric_Surface_Model_Saddles', source_surface_model_saddle)
    Writer.write_soundings_file('Bathymetric_Surface_Model_Minimas', source_surface_model_minima)

########################################################################################################################

    # Cartographic model analysis (hydrographic sounding selection)
    log.info('-Processing Hydrographic Sounding Selection')

    # Initialize Tree class
    log.info('\t--Building PR-Quadtree for Source Soundings')
    source_capacity = int(ceil(source_pointset.get_vertices_num() * 0.0004))
    source_tree = Tree(source_capacity)
    source_tree.build_point_tree(source_pointset)

    # Remove legibility issues with danger to navigation points
    log.info('\t--Removing Legibility Violations with Danger to Navigation Points')
    source_soundings.sort(key=lambda k: k.z_value)
    while len(dangers) > 0:
        legibility_violations = list()
        source_tree.generalization(source_tree.get_root(), 0, source_pointset.get_domain(), dangers[0], source_pointset,
                                   legibility_violations, 'DCM', scale, horiz_spacing, vert_spacing)

        # Delete generalized soundings from sorted vertex list
        for legibility_violation in legibility_violations:
            delete_idx = modified_binary_search(source_soundings, legibility_violation)
            del source_soundings[delete_idx]
        del dangers[0]

    # Read combined source and chart soundings into point set; removes legibility issues near survey boundary
    log.info('\t--Combining Source and Chart Soundings')
    source_chart = source_soundings + chart_soundings
    source_chart_pointset = Reader.read_vertex_list_to_pointset(source_chart)

    # Initialize Tree class
    log.info('\t\t--Building PR-Quadtree')
    source_chart_capacity = int(ceil(source_chart_pointset.get_vertices_num() * 0.0004))
    source_chart_tree = Tree(source_chart_capacity)
    source_chart_tree.build_point_tree(source_chart_pointset)

    # Sort list of source/chart soundings from low to high
    source_chart_sorted = sorted(source_chart, key=lambda k: k.z_value)

    # list to store hydrographic selection
    hydro_chart_soundings = list()

    log.info('\t--Selecting Label-Based Hydrographic Sounding Selection from Source and Chart Soundings')
    if horiz_spacing == 0.75:
        log.info('\t\t--Horizontal Character Spacing Set to Default 0.75 mm')
    else:
        log.info('\t\t--Horizontal Character Spacing Set to {} mm'.format(horiz_spacing))

    if vert_spacing == 0.75:
        log.info('\t\t--Vertical Character Spacing Set to Default {} mm'.format(vert_spacing))
    else:
        log.info('\t\t--Vertical Character Spacing Set to {} mm'.format(vert_spacing))

    # Label-based generalization
    while len(source_chart_sorted) > 0:
        delete_list = list()
        source_chart_tree.generalization(source_chart_tree.get_root(), 0, source_chart_pointset.get_domain(),
                                         source_chart_sorted[0], source_chart_pointset, delete_list, 'DCM',
                                         scale, horiz_spacing, vert_spacing)

        # Delete generalized soundings from sorted vertex list
        for i in delete_list:
            delete_idx = modified_binary_search(source_chart_sorted, i)  # Binary search increases performance
            del source_chart_sorted[delete_idx]
        hydro_chart_soundings.append(source_chart_sorted[0])
        del source_chart_sorted[0]

    # Remove chart soundings from hydrographic selection
    hydro_soundings = [sounding for sounding in hydro_chart_soundings if sounding not in chart_soundings]

    log.info('\t\t--Hydrographic Sounding Selection Count: ' + str(len(hydro_soundings)))

    log.info('\t\t--Extracting Generalized ENC Soundings')
    generalized_chart_soundings = [sounding for sounding in hydro_chart_soundings if sounding in chart_soundings]
    Writer.write_soundings_file('generalized_chart', generalized_chart_soundings)

    generalized_chart_pointset = Reader.read_vertex_list_to_pointset(generalized_chart_soundings)
    generalized_chart = generalized_chart_pointset.get_all_vertices()
    for vertex in generalized_chart_soundings:
        target_label = get_carto_symbol(vertex, scale, horiz_spacing, vert_spacing)[1]
        Writer.write_wkt_file('Generalized_Chart_DCM_WKT.txt', target_label.wkt)

    log.info('\t\t\t--Building PR-Quadtree for Generalized ENC Soundings')
    generalized_chart_capacity = int(ceil(len(generalized_chart) * 0.004))
    generalized_chart_tree = Tree(generalized_chart_capacity)
    generalized_chart_tree.build_point_tree(generalized_chart_pointset)

    # Write output files
    log.info('\t\t--Writing Hydrographic Sounding Selection Files')
    hydro_out_name = str(source).split('.')[0] + '_HydroSelect'
    Writer.write_soundings_file(hydro_out_name, hydro_soundings)
    for vertex in hydro_soundings:
        target_label = get_carto_symbol(vertex, scale, horiz_spacing, vert_spacing)[1]
        Writer.write_wkt_file(hydro_out_name + '_DCM_WKT.txt', target_label.wkt)

    log.info('-Hydrographic Sounding Selection Complete')

########################################################################################################################

    # Cartographic model analysis (cartographic sounding selection)
    log.info('-Processing Cartographic Sounding Selection')
    log.info('\t--Selecting Least Depth Soundings')

    log.info('\t\t--Building PR-Quadtree for Danger to Navigation Points, Source Soundings, and Existing ENC Soundings')
    source_chart_dangers_tree = Tree(source_chart_dangers_capacity)
    source_chart_dangers_pointset = Reader.read_vertex_list_to_pointset(source_chart_dangers)
    source_chart_dangers_tree.build_point_tree(source_chart_dangers_pointset)

    # Select shallowest sounding inside each closed depth contour if no legibility violations with existing soundings
    least_depths = list()
    for shape_record in contours.iterShapeRecords(fields=['VALDCO']):
        contour_geojson = shape_record.shape.__geo_interface__
        contour_linestring = shape(contour_geojson)
        contour_x, contour_y = contour_linestring.coords.xy
        inside_contour_soundings = list()

        # Proceed if contour is closed
        if contour_x[0] == contour_x[-1] and contour_y[0] == contour_y[-1]:
            contour_polygon = Polygon(contour_linestring)
            source_chart_dangers_tree.points_in_polygon(source_chart_dangers_tree.get_root(), 0,
                                                        source_chart_dangers_pointset.get_domain(), contour_polygon,
                                                        source_chart_dangers_pointset, inside_contour_soundings)

            # Shallowest maxima inside closed depth contour
            if len(inside_contour_soundings) > 0:
                inside_contour_soundings.sort(key=lambda k: k.z_value)
                least_depth = inside_contour_soundings[0]

                legibility_violations = check_vertex_legibility(least_depth, generalized_chart_tree,
                                                                generalized_chart_pointset, scale, horiz_spacing,
                                                                vert_spacing)

                # Select least depth sounding if no legibility violation with ENC or shallower than ENC sounding
                if len(legibility_violations) > 0:
                    legibility_violations.sort(key=lambda k: k.z_value)
                    if legibility_violations[0].z_value > least_depth.z_value:
                        if least_depth not in least_depths:  # Nested contours can result in duplicates
                            if least_depth.s57_type is None:
                                least_depth.sounding_type = 'least_depth'
                                least_depths.append(least_depth)
                else:
                    if least_depth not in least_depths:  # Nested contours can result in duplicates
                        if least_depth.s57_type is None:
                            least_depth.sounding_type = 'least_depth'
                            least_depths.append(least_depth)

    # Evaluate legibility constraint for least depth soundings
    least_depth_capacity = int(ceil(len(least_depths) * 0.004))
    least_depth_tree = Tree(least_depth_capacity)
    least_depth_pointset = Reader.read_vertex_list_to_pointset(least_depths)
    least_depth_tree.build_point_tree(least_depth_pointset)

    least_depth_legibility_violations = validate_legibility_constraint(least_depths, least_depth_tree,
                                                                       least_depth_pointset, scale, horiz_spacing,
                                                                       vert_spacing)

    log.info('\t\t\t--Least Depth Count: ' + str(len(least_depths)))
    log.info('\t\t\t--Least Depth Legibility Violations: ' + str(len(least_depth_legibility_violations)))

    # Write output files
    Writer.write_soundings_file('Least_Depth_Soundings', least_depths)

    # Select shoal, supporting, and deep soundings present in the hydrographic selection
    log.info('\t--Selecting Shoal, Supporting, and Deep Soundings')
    hydro_shoal_soundings = [v for v in source_chart if v.sounding_type is 'Maxima' and v in hydro_soundings
                             and v.sounding_type != 'least_depth']
    for hydro_shoal in hydro_shoal_soundings:
        hydro_shoal.sounding_type = 'shoal'

    hydro_supporting_soundings = [v for v in source_chart if v.sounding_type is 'Saddle' and v in hydro_soundings]
    for hydro_supporting in hydro_supporting_soundings:
        hydro_supporting.sounding_type = 'supporting'

    hydro_deep_soundings = [v for v in source_chart if v.sounding_type is 'Minima' and v in hydro_soundings]
    for hydro_deep in hydro_deep_soundings:
        hydro_deep.sounding_type = 'deep'

    # Select soundings with no legibility issues with least depth soundings
    selection = least_depths[:]
    hydro_critical_points = hydro_shoal_soundings + hydro_supporting_soundings + hydro_deep_soundings
    hydro_critical_points.sort(key=lambda k: k.z_value)
    for critical_point in hydro_critical_points:
        legibility_violations = check_vertex_legibility(critical_point, least_depth_tree, least_depth_pointset,
                                                        scale, horiz_spacing, vert_spacing)

        if len(legibility_violations) == 0:
            selection.append(critical_point)

    # Report counts
    shoal_soundings = [v for v in selection if v in hydro_shoal_soundings]
    supporting_soundings = [v for v in selection if v in hydro_supporting_soundings]
    deep_soundings = [v for v in selection if v in hydro_deep_soundings]
    log.info('\t\t\t--Shoal Sounding Count: ' + str(len(shoal_soundings)))
    log.info('\t\t\t--Supporting Sounding Count: ' + str(len(supporting_soundings)))
    log.info('\t\t\t--Deep Sounding Count: ' + str(len(deep_soundings)))

    # Write output files
    Writer.write_soundings_file('Shoal_Soundings', shoal_soundings)
    Writer.write_soundings_file('Supporting_Soundings', supporting_soundings)
    Writer.write_soundings_file('Deep_Soundings', deep_soundings)

    # Select fill soundings using variable length radius-based method
    log.info('\t\t--Selecting Fill Soundings (Radius)')

    # Sort hydrographic selection from shallow to deep
    potential_radius_fill_sorted = sorted(hydro_soundings, key=lambda k: k.z_value)
    potential_radius_fill_count = len(potential_radius_fill_sorted)

    # Create lookup list for radius length
    radius_lengths = [float(starting_radius) + x * (float(ending_radius) - float(starting_radius)) /
                      potential_radius_fill_count for x in range(potential_radius_fill_count)]

    radius_dict = dict()
    for i in range(potential_radius_fill_count):
        radius_dict[potential_radius_fill_sorted[i].__str__()] = radius_lengths[i]

    # Radius-based generalization
    potential_radius_fill_point_set = Reader.read_vertex_list_to_pointset(potential_radius_fill_sorted)
    potential_radius_fill_capacity = int(ceil(potential_radius_fill_point_set.get_vertices_num() * 0.0004))
    potential_radius_fill_tree = Tree(potential_radius_fill_capacity)
    potential_radius_fill_tree.build_point_tree(potential_radius_fill_point_set)

    radius_fill = list()
    while len(potential_radius_fill_sorted) > 0:
        delete_list = list()
        potential_radius_fill_tree.generalization(potential_radius_fill_tree.get_root(), 0,
                                                  potential_radius_fill_point_set.get_domain(),
                                                  potential_radius_fill_sorted[0], potential_radius_fill_point_set,
                                                  delete_list, 'Radius', radius_lookup=radius_dict)

        # Delete generalized soundings from sorted vertex list
        for delete in delete_list:
            delete_idx = modified_binary_search(potential_radius_fill_sorted, delete)
            if delete_idx is not None:  # Depth precision issue where radius increases but same depth
                del potential_radius_fill_sorted[delete_idx]
        radius_fill.append(potential_radius_fill_sorted[0])
        del potential_radius_fill_sorted[0]

    least_depth_shoal_supporting_deep = least_depths + shoal_soundings + supporting_soundings + deep_soundings
    radius_fill_soundings = [fill for fill in radius_fill if fill not in least_depth_shoal_supporting_deep]

    # Select fill soundings that do not overplot with least depth soundings
    for radius_fill in radius_fill_soundings:
        legibility_violations = check_vertex_legibility(radius_fill, least_depth_tree, least_depth_pointset,
                                                        scale, horiz_spacing, vert_spacing)
        if len(legibility_violations) == 0:
            radius_fill.sounding_type = 'fill_radius'
            selection.append(radius_fill)

    # Report count of fill soundings (radius)
    radius_fill_count = len(selection) - len(least_depth_shoal_supporting_deep)
    log.info('\t\t--Fill Soundings (Radius) Count: ' + str(radius_fill_count))

    # Extract edges for constraining the triangulation
    all_segment_vertices, all_idx_list, holes, bathy_extent, dredged_extent = get_feature_segments(contours,
                                                                                                   depth_polygons,
                                                                                                   boundary=False)

    # Triangulate shoal, supporting, deep, radius-fill, existing ENC soundings, and depth contours
    log.info('\t\t\t--Triangulating Current Selection, Generalized ENC Soundings, Danger to Navigation Points,'
             ' and Depth Contours')
    selection_chart_dangers = selection + generalized_chart + dangers_with_depth
    selection_chart_dangers_contour = selection_chart_dangers + all_segment_vertices
    selection_chart_dangers_contour_tri = triangulate(selection_chart_dangers, all_segment_vertices, all_idx_list,
                                                      holes)
    selection_chart_dangers_contour_tin = Reader.read_triangulation(selection_chart_dangers_contour_tri,
                                                                    selection_chart_dangers_contour)
    selection_chart_dangers_contour_capacity = int(ceil(len(selection_chart_dangers) * 0.004))
    selection_chart_dangers_contour_tree = Tree(selection_chart_dangers_contour_capacity)
    selection_chart_dangers_contour_tree.build_tin_tree(selection_chart_dangers_contour_tin)

    log.info('\t\t\t--Selecting Fill Soundings (CATZOC)')
    hydro_point_set = Reader.read_vertex_list_to_pointset(hydro_soundings)
    hydro_capacity = int(ceil(hydro_point_set.get_vertices_num() * 0.0004))
    hydro_tree = Tree(hydro_capacity)
    hydro_tree.build_point_tree(hydro_point_set)

    catzoc_fill_soundings = list()
    selection_chart_dangers_contour_tree.calculate_fill_soundings(selection_chart_dangers_contour_tree.get_root(), 0,
                                                                  selection_chart_dangers_contour_tin.get_domain(),
                                                                  hydro_tree, hydro_point_set,
                                                                  selection_chart_dangers_contour_tin,
                                                                  catzoc_fill_soundings)

    # Select soundings that do not have legibility issues with least depth soundings
    catzoc_fill_legibility_violations = list()
    if len(catzoc_fill_soundings) > 0:
        while len(catzoc_fill_soundings) > 0:
            for catzoc_fill in catzoc_fill_soundings:
                if catzoc_fill not in catzoc_fill_legibility_violations:
                    legibility_violations = check_vertex_legibility(catzoc_fill, least_depth_tree,
                                                                    least_depth_pointset, scale, horiz_spacing,
                                                                    vert_spacing)
                    if len(legibility_violations) == 0:
                        catzoc_fill.sounding_type = 'fill_catzoc'
                        selection.append(catzoc_fill)
                    else:
                        catzoc_fill_legibility_violations.append(catzoc_fill)

            selection_chart_dangers = selection + generalized_chart + dangers_with_depth
            selection_chart_dangers_contour = selection_chart_dangers + all_segment_vertices
            selection_chart_dangers_contour_tri = triangulate(selection_chart_dangers, all_segment_vertices,
                                                              all_idx_list, holes)

            selection_chart_dangers_contour_tin = Reader.read_triangulation(selection_chart_dangers_contour_tri,
                                                                            selection_chart_dangers_contour)
            selection_chart_dangers_contour_tree = Tree(selection_chart_dangers_contour_capacity)
            selection_chart_dangers_contour_tree.build_tin_tree(selection_chart_dangers_contour_tin)

            fill_soundings = list()
            selection_chart_dangers_contour_tree.calculate_fill_soundings(selection_chart_dangers_contour_tree.get_root(), 0,
                                                                          selection_chart_dangers_contour_tin.get_domain(),
                                                                          hydro_tree,  hydro_point_set,
                                                                          selection_chart_dangers_contour_tin,
                                                                          fill_soundings)

            catzoc_fill_soundings = [f for f in fill_soundings if f not in catzoc_fill_legibility_violations]

    # Report fill (CATZOC) sounding count
    non_catzoc_count = len(least_depth_shoal_supporting_deep) + radius_fill_count
    log.info('\t\t--Fill Soundings (CATZOC) Count: ' + str(len(selection) - non_catzoc_count))

########################################################################################################################

    # Adjust selection for cartographic constraint violations

    # Evaluate functionality constraint for non-adjusted soundings
    log.info('\t--Adjusting Cartographic Selection for Legibility and Functionality Violations')

    log.info('\t\t--Adjusting Cartographic Selection for Legibility Violations with Sounding Labels and Depth Contours')
    # Select fill soundings that do not overplot with depth contours or least depth soundings
    contour_overplot = list()
    for sounding in selection:
        if sounding not in least_depths:
            label_no_spacing = get_carto_symbol(sounding, scale, 0, 0)[1]
            for shape_record in contours.iterShapeRecords(fields=['VALDCO']):
                contour_depth = shape_record.record[0]
                if sounding.z_value >= contour_depth:
                    contour_geojson = shape_record.shape.__geo_interface__
                    contour_linestring = shape(contour_geojson)
                    if label_no_spacing.intersects(contour_linestring):
                        contour_overplot.append(sounding)
                        break

    for overplot_sounding in contour_overplot:
        selection.remove(overplot_sounding)

    outside_range = list()
    for shape_record in depth_polygons.iterShapeRecords(fields=['DRVAL2']):
        drval2 = shape_record.record[0]
        depare_geojson = shape_record.shape.__geo_interface__
        depare_polygon = shape(depare_geojson)
        for sounding in selection:
            if sounding.z_value > drval2:
                if depare_polygon.intersects(Point(sounding.x_value, sounding.y_value)):
                    outside_range.append(sounding)

    for i in outside_range:
        selection.remove(i)

    log.info('\t--Evaluating Cartographic Constraint Violations for Preliminary Selection')

    selection_chart_dangers_contour_funct_viol = validate_functionality_constraint(selection_chart_dangers_contour_tin,
                                                                                   source_chart_dangers_tree,
                                                                                   source_chart_dangers_pointset,
                                                                                   depth_polygons, validation_method)

    # Evaluate legibility constraint for currently selected soundings
    selection_capacity = int(ceil(len(selection) * 0.004))
    selection_tree = Tree(selection_capacity)
    selection_pointset = Reader.read_vertex_list_to_pointset(selection)
    selection_tree.build_point_tree(selection_pointset)

    selection_legibility_violations = validate_legibility_constraint(selection, selection_tree, selection_pointset,
                                                                     scale, horiz_spacing, vert_spacing)

    # Write output file
    Writer.write_tin_file(selection_chart_dangers_contour_tin, 'Preliminary_Selection_Chart_Danger_Contour_TIN')

    # Adjust for functionality (safety) violations
    if len(selection_chart_dangers_contour_funct_viol) == 0 and len(selection_legibility_violations) == 0:
        log.info('\t\t--Functionality Violations: ' + str(len(selection_chart_dangers_contour_funct_viol)))
        log.info('\t\t--Legibility Violations: ' + str(len(selection_legibility_violations)))
        log.info('\t--Final Cartographic Selection Count: ' + str(len(selection)))
    else:
        log.info('\t\t--Functionality Violations: ' + str(len(selection_chart_dangers_contour_funct_viol)))
        log.info('\t\t--Legibility Violations: ' + str(len(selection_legibility_violations)))
        log.info('\t\t--Initial Cartographic Selection Count: ' + str(len(selection)))
        log.info('\t-Adjusting Cartographic Selection for Functionality Violations')

        functionality_violations_sorted = sorted(selection_chart_dangers_contour_funct_viol, key=lambda k: k.z_value)
        iteration_count = 0
        functionality_violation_count = list()
        while len(functionality_violations_sorted) > 0:
            selection.sort(key=lambda k: k.z_value)
            functionality_violations = functionality_violations_sorted[:]
            # Label-based generalization
            while len(functionality_violations_sorted) > 0:
                legibility_violations = list()
                selection_tree.generalization(selection_tree.get_root(), 0, selection_pointset.get_domain(),
                                              functionality_violations_sorted[0], selection_pointset,
                                              legibility_violations, 'DCM', scale, horiz_spacing, vert_spacing)

                # Delete generalized soundings from sorted vertex list
                for legibility_violation in legibility_violations:
                    if legibility_violation not in least_depths:
                        delete_idx = modified_binary_search(selection, legibility_violation)
                        del selection[delete_idx]
                del functionality_violations_sorted[0]

            for violation in functionality_violations:
                selection_tree = Tree(selection_capacity)
                selection_pointset = Reader.read_vertex_list_to_pointset(selection)
                selection_tree.build_point_tree(selection_pointset)

                legibility_violations = check_vertex_legibility(violation, selection_tree, selection_pointset, scale,
                                                                horiz_spacing, vert_spacing)

                if len(legibility_violations) == 0:
                    violation.sounding_type = 'adjustment'
                    selection.append(violation)
                else:
                    if iteration_count >= 3 and functionality_violation_count[-1] == functionality_violation_count[-2]:
                        violation.sounding_type = 'adjustment'
                        selection.append(violation)
                        break
                    elif iteration_count >= 5:
                        violation.sounding_type = 'adjustment'
                        selection.append(violation)
                        break
            selection_chart_dangers = selection + generalized_chart + dangers_with_depth
            selection_chart_dangers_contour = selection_chart_dangers + all_segment_vertices
            selection_chart_dangers_contour_tri = triangulate(selection_chart_dangers, all_segment_vertices,
                                                              all_idx_list, holes)
            selection_chart_dangers_contour_tin = Reader.read_triangulation(selection_chart_dangers_contour_tri,
                                                                            selection_chart_dangers_contour)

            selection_chart_dangers_contour_funct_viol = validate_functionality_constraint(selection_chart_dangers_contour_tin,
                                                                                           source_chart_dangers_tree,
                                                                                           source_chart_dangers_pointset,
                                                                                           depth_polygons,
                                                                                           validation_method)

            functionality_violations_sorted = sorted(selection_chart_dangers_contour_funct_viol, key=lambda k: k.z_value)
            functionality_violation_count.append(len(functionality_violations_sorted))

            selection_capacity = int(ceil(len(selection) * 0.004))
            selection_tree = Tree(selection_capacity)
            selection_pointset = Reader.read_vertex_list_to_pointset(selection)
            selection_tree.build_point_tree(selection_pointset)

            selection_legibility_violations = validate_legibility_constraint(selection, selection_tree,
                                                                             selection_pointset, scale, horiz_spacing,
                                                                             vert_spacing)
            iteration_count += 1
            log.info('\t\t--Iteration Count: ' + str(iteration_count))
            log.info('\t\t--Count: ' + str(len(selection)))
            log.info('\t\t--Functionality Violations: ' + str(len(functionality_violations_sorted)))
            log.info('\t\t--Legibility Violations: ' + str(len(selection_legibility_violations)))

        # Evaluate legibility constraint for adjusted sounding set
        selection_capacity = int(ceil(len(selection) * 0.004))
        selection_tree = Tree(selection_capacity)
        selection_pointset = Reader.read_vertex_list_to_pointset(selection)
        selection_tree.build_point_tree(selection_pointset)

        selection_legibility_violations = validate_legibility_constraint(selection, selection_tree, selection_pointset,
                                                                         scale, horiz_spacing, vert_spacing)

        selection_chart_dangers = selection + generalized_chart + dangers_with_depth
        selection_chart_dangers_contour = selection_chart_dangers + all_segment_vertices
        selection_chart_dangers_contour_tri = triangulate(selection_chart_dangers, all_segment_vertices,
                                                          all_idx_list, holes)
        selection_chart_dangers_contour_tin = Reader.read_triangulation(selection_chart_dangers_contour_tri,
                                                                        selection_chart_dangers_contour)

        selection_chart_dangers_contour_funct_viol_tri = validate_functionality_constraint(selection_chart_dangers_contour_tin,
                                                                                       source_chart_dangers_tree,
                                                                                       source_chart_dangers_pointset,
                                                                                       depth_polygons,
                                                                                       validation_method)

        selection_chart_dangers_contour_funct_viol_surf = validate_functionality_constraint(selection_chart_dangers_contour_tin,
                                                                                       source_chart_dangers_tree,
                                                                                       source_chart_dangers_pointset,
                                                                                       depth_polygons,
                                                                                       'SURFACE')

        log.info('\t\t--Final Triangle Functionality Violations: ' + str(len(selection_chart_dangers_contour_funct_viol_tri)))
        log.info('\t\t--Final Shallow Surface Functionality Violations: ' + str(len(selection_chart_dangers_contour_funct_viol_surf)))
        log.info('\t\t--Final Legibility Violations: ' + str(len(selection_legibility_violations)))
        log.info('\t\t--Final Cartographic Selection Count: ' + str(len(selection)))

########################################################################################################################

    # Write output files
    log.info('\t--Writing Cartograhic Output Files')
    if len(selection_legibility_violations) > 0:
        Writer.write_soundings_file('Cartographic_Selection_Legibility_Violations', selection_legibility_violations)
    if len(selection_chart_dangers_contour_funct_viol) > 0:  # Should always be zero
        Writer.write_soundings_file('Cartographic_Selection_Functionality_Violations',
                                    selection_chart_dangers_contour_funct_viol)

    carto_out_name = str(source).split('.')[0] + '_CartoSelect'
    carto_selection = [sounding for sounding in selection if sounding not in dangers_with_depth]
    Writer.write_soundings_file(carto_out_name, carto_selection)
    for vertex in carto_selection:
        target_label = get_carto_symbol(vertex, scale, horiz_spacing, vert_spacing)[1]
        Writer.write_wkt_file(carto_out_name + '_DCM_WKT.txt', target_label.wkt)

    selection_chart_dangers = selection + generalized_chart + dangers_with_depth
    selection_chart_dangers_contour = selection_chart_dangers + all_segment_vertices
    selection_chart_dangers_contour_tri = triangulate(selection_chart_dangers, all_segment_vertices,
                                                      all_idx_list, holes)
    selection_chart_dangers_contour_tin = Reader.read_triangulation(selection_chart_dangers_contour_tri,
                                                                    selection_chart_dangers_contour)

    Writer.write_tin_file(selection_chart_dangers_contour_tin, carto_out_name + 'Selection_TIN')

    return


if __name__ == '__main__':
    main()
