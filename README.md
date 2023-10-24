# Sounding Selection #
Cartographic sounding selection is a constraint-based bathymetric generalization process for identifying navigationally relevant soundings for nautical chart display. Electronic Navigational Charts (ENCs) are the premier maritime navigation medium and are produced according to international standards and distributed around the world. Cartographic generalization for ENCs is a major bottleneck in the chart creation and update process, where high volumes of data collected from constantly changing seafloor topographies require tedious examination. Moreover, these data are provided by multiple sources from various collection platforms at different levels of quality, further complicating the generalization process. Therefore, in this work, we present a comprehensive sounding selection algorithm focused on safe navigation that leverages both the Digital Surface Model (DSM) of multi-source bathymetry and the cartographic portrayal of the ENC. We define a taxonomy and hierarchy of soundings found on ENCs and employ methods to identify these soundings. Furthermore, we explore how depth contour generalization can significantly impact sounding selection distribution. We incorporate additional ENC bathymetric features (rocks, wrecks, and obstructions) affecting sounding distribution, calculate metrics from current chart products, and introduce procedures to correct cartographic constraint violations to ensure a shoal-bias and mariner-readable output. This results in a selection that is near navigationally ready and complementary to the specific waterways of the area, contributing to the complete automation of the ENC creation and update process for safer maritime navigation.

### Reference Papers ###
+ Dyer, N., Kastrisios, C., & De Floriani, L. (2023). Chart Features, Data Quality, and Scale in Cartographic Sounding Selection from Composite Bathymetric Data. Geo-spatial Information Science. DOI: https://doi.org/10.1080/10095020.2023.2266222
+ Kastrisios, C., Dyer, N., Nada, T., Stilianos, C., & Cordero, J. (2023). Increasing Efficiency of Nautical Chart Production and Accessibility to Marine Environment Data Through an Open-Science Compilation Workflow. ISPRS International Journal of Geo-Information, 12(3), 116. DOI: https://doi.org/10.3390/ijgi12030116
+ Dyer, N., Kastrisios, C., & De Floriani, L. (2022). Label-based generalization of bathymetry data for hydrographic sounding selection. Cartography and Geographic Information Science, 49(4), 338-353. DOI: https://doi.org/10.1080/15230406.2021.2014974

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
