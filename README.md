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
python main.py -i Source_Soundings_xyzc.txt -c ENC_Soundings_xyzc.txt -r 40000 -v triangle -d DepthsL_Contours.shp -a DepthsA_Areas.shp -n DangersP_Points.shp -s 43.03 -e 1309.28
```
Example data file formats can be found in the ```data``` directory.

### Parameters Description ###
```
 -i <inputfile> -r <scale> -v <validation> -c <chart_soundings> -a <depth_areas> -d <depth_contours> -n <dangers_to_navigation> -s <starting_radius_length> -e <ending_radius_length> -x <horizontal_spacing> -y <vertical_spacing>
```
```-i``` *Input Soundings File* | **Required** | X,Y,Z,C Text File Format</br>
```-r``` *Scale* | **Required** | Integer</br>
```-v``` *Safety Validation Method* | **Required** | TRIANGLE or SURFACE String</br>
```-c``` *Current ENC Soundings* | **Required** | X,Y,Z,C Text File Format</br>
```-a``` *DepthsA Polygons* | **Required** | Polygon Shapefile in S-57 Attributes</br>
```-d``` *DepthsL Polylines* | **Required** | Polyline Shapefile in S-57 Attributes</br>
```-n``` *DangersP Points* | **Required** | Point Shapefile with S-57 Attributes</br>
```-s``` *Starting Radius Length* | **Required** | Starting Radius Length for Fill Soundings</br>
```-e``` *Ending Radius Length* | **Required** | Ending Radius Length for Fill Soundings</br>
```-x``` *Horizontal Spacing Between Labels* | **Optional** | Float</br>
```-y``` *Vertical Spacing Between Labels* | **Optional** | Float</br>

**Notes:**
<p>A default horizontal/vertical spacing of 0.75 mm to the scale is used unless a different value is provided.</p>
An output log file is also created during execution.

### Requirements ###
+ Triangle (https://rufat.be/triangle/)
    * Python wrapper of Triangle (http://www.cs.cmu.edu/~quake/triangle.html)
+ Shapely >= 1.8.0
+ Numpy >= 1.21.5
+ 3.6 <= Python < 3.9
