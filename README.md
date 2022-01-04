# Hydrographic Sounding Selection #
Hydrographic sounding selection is the process of generalizing high-resolution bathymetry data to produce a shoal-biased and dense, yet manageable, subset of soundings without label over-plot that can support nautical chart compilation or bathymetric modelling. This algorithm improves over existing methods by generalizing bathymetry using the physical dimensions of symbolized depth values at scale.
### Reference Paper ###
Dyer, N., Kastrisios, C., & De Floriani, L. (2021). Label-Based Generalization of Bathymetry Data for Hydrographic Sounding Selection. Cartography and Geographic Information Science.  https://doi.org/10.1080/15230406.2021.2014974.

**Note:** Several enhancments have been implemented to eliminate remaining functionality constraint violations.
### Requirements ###
+ Triangle (https://rufat.be/triangle/)
    * Python wrapper of Triangle (http://www.cs.cmu.edu/~quake/triangle.html)
+ Shapely >= 1.8.0
+ Numpy >= 1.21.5
+ 3.6 <= Python < 3.9
