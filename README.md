# Sounding Selection #
Hydrographic sounding selection is the process of generalizing high-resolution bathymetry data to produce a shoal-biased and dense, yet manageable, subset of soundings without label over-plot that can support nautical chart compilation or bathymetric modelling. This algorithm improves over existing methods by generalizing bathymetry using the physical dimensions of symbolized depth values at scale.

### Reference Paper ###
Dyer, N., Kastrisios, C., & De Floriani, L. (2021). Label-Based Generalization of Bathymetry Data for Hydrographic Sounding Selection. Cartography and Geographic Information Science. DOI: https://doi.org/10.1080/15230406.2021.2014974.

**Note:** Several enhancments have been implemented to eliminate remaining functionality constraint violations.

### Installation ###
Once in the root of the repository, enter into the command line:
```
python setup.py install  # installs to current Python environment (including required libraries)
```
You should then be able to execute the program from the command line as such:
```
sounding_selection -i path\to\data\Bathymetry_xyz.txt -s 25000 -m path\to\data\Bathymetry_Boundary.txt
```
Example data file formats can be found in the ```data``` directory.

### Parameters Description ###
```
-i <inputfile> -s <scale> -m <m_qual> -x <horizontal_spacing> -y <vertical_spacing>
```
```-i``` *Input Soundings File* | **Required** | X,Y,Z Text File Format</br>
```-s``` *Scale* | **Required** | Integer</br>
```-m``` *Survey Boundary (M_QUAL) Polygon* | **Optional** | Polygon WKT in Text File Format</br>
```-x``` *Horizontal Spacing Between Labels* | **Optional** | Float</br>
```-y``` *Vertical Spacing Between Labels* | **Optional** | Float</br>

**Notes:**
<p>When a survey polygon is provided, the triangulation performed for validation (see reference paper) is constrained to the polygon. If it is not provided, the triangulation is Delaunay.</p>
<p>A default horizontal/vertical spacing of 0.75 mm to the scale is used unless a different value is provided.</p>
An output log file is also created during execution.

### Requirements ###
+ Triangle (https://rufat.be/triangle/)
    * Python wrapper of Triangle (http://www.cs.cmu.edu/~quake/triangle.html)
+ Shapely >= 1.8.0
+ Numpy >= 1.21.5
+ 3.6 <= Python < 3.9
