# Hydrographic-Sounding-Selection
## How to execute
*Tested in Python 3.5.3
**Requires Shapely and Triangle (Python wrapper) libraries
## Shapely
# https://shapely.readthedocs.io/en/latest/
## Triangle Python wrapper
# https://rufat.be/triangle/
## Triangle source: Shewchuk, J. R. (1996, May). Triangle: Engineering a 2D quality mesh generator and Delaunay triangulator. 
## In Workshop on Applied Computational Geometry (pp. 203-222). Springer, Berlin, Heidelberg.
# http://www.cs.cmu.edu/~quake/triangle.html

Navigate to directory containing the input files and Python code. Using the command prompt enter:

python main.py -i <inputfile> -s <scale> -m <m_qual> -x <horizontal_spacing> -y <vertical_spacing>

flags:
-h help
-i input soundings (x,y,z format)
-s scale (integer, no comma)
-m m_qual (text file in WKT format; optional)
-x horizontal spacing between labels (0.75 mm @ scale is default)
-y vertical spacing between labels (0.75 mm @ scale is default)

Examples used in this study:

cd /c/path/to/data_and_py_location

python main.py -i H11861_xyz.txt -s 20000
python main.py -i H11988_xyz.txt -s 20000
python main.py -i H12018_xyz.txt -s 40000
python main.py -i H12626_xyz.txt -s 25000

Example outputs:

## Without M_QUAL (delaunay triangulation for validation)

python main.py -i H11861_xyz.txt -s 20000

[WARNING] M_QUAL Not Provided
-Reading Source Soundings File
-Building PR-Quadtree
-Processing Label-Based Generalization
        --Generalization Time:  18 minutes, 26 seconds
-Evaluating Cartographic Constraint Violations
        --Initial Generalized Soundings Count:  1898
        --Initial Functionality (Safety) Constraint Violations:  179
        --Initial Legibility Violations:  0
-Adjusting Selection for Functionality (Safety) Constraint Violations
        --Iteration Count: 1
                --Violations: 47
        --Iteration Count: 2
                --Violations: 1
        --Iteration Count: 3
                --Violations: 0
                --Final Generalized Soundings Count:  1946
                --Final Iteration Adjusted Functionality (Safety) Violations: 0
                --Final Iteration Adjusted Legibility Violations:  483
-Writing Adjusted Generalized Soundings File
-Writing Label Polygon Files
-Writing Constraint Violation Files
-Hydrographic Sounding Selection Complete


## With M_QUAL (constrained delaunay triangulation for validation)

python main.py -i H11528_xyz.txt -s 20000 -m H11528_Boundary.txt

-Reading Source Soundings File
-Reading M_QUAL File
-Building PR-Quadtree
-Processing Label-Based Generalization
        --Generalization Time:  07 minutes, 48 seconds
-Evaluating Cartographic Constraint Violations
        --Initial Generalized Soundings Count:  529
        --Initial Functionality (Safety) Constraint Violations:  136
        --Initial Legibility Violations:  0
-Adjusting Selection for Functionality (Safety) Constraint Violations
        --Iteration Count: 1
                --Violations: 97
        --Iteration Count: 2
                --Violations: 8
        --Iteration Count: 3
                --Violations: 1
        --Iteration Count: 4
                --Violations: 0
                --Final Generalized Soundings Count:  635
                --Final Iteration Adjusted Functionality (Safety) Violations: 0
                --Final Iteration Adjusted Legibility Violations:  346
-Writing Adjusted Generalized Soundings File
-Writing Label Polygon Files
-Writing Constraint Violation Files
-Hydrographic Sounding Selection Complete
