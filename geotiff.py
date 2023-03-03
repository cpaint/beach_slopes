# 
#
"""
1. load in lidar data
2. transpose to a new local coordinate system
3. transform into shore normal coordinate system using rotation trig
4. select for subset of lidar data at the beach

5. select every ?X meters and create cross-shore transects
6. fit a line to the transects
7. load in LZMST data to compare
"""
import numpy as np
import laspy
import pandas as pd
import matplotlib.pyplot as plt
from osgeo import gdal, osr


# Import Data
ds = gdal.Open('Data/socal_coned_Job822412/Job822412_socal_coned.tif', gdal.GA_ReadOnly)
gt = ds.GetGeoTransform()
rd = ds.GetRasterBand(1)
data = rd.ReadAsArray()
old_cs= osr.SpatialReference()
print('coordsys:', old_cs)
old_cs.ImportFromWkt(ds.GetProjectionRef())

# create the new coordinate system
wgs84_wkt = """
GEOGCS["WGS 84",
    DATUM["WGS_1984",
        SPHEROID["WGS 84",6378137,298.257223563,
            AUTHORITY["EPSG","7030"]],
        AUTHORITY["EPSG","6326"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.01745329251994328,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4326"]]"""
new_cs = osr.SpatialReference()
new_cs .ImportFromWkt(wgs84_wkt)

width = ds.RasterXSize
height = ds.RasterYSize
print('width:', width)
print('height:',height)
print(gt)
print(gt)
minx = gt[0]
miny = gt[3] + width*gt[4] + height*gt[5] 
maxx = gt[0] + width*gt[1] + height*gt[2]
maxy = gt[3] 

transform = osr.CoordinateTransformation(old_cs,new_cs)
latlon = transform.TransformPoint(minx,miny)
print(latlon)

print(data)
#data = np.where((data < 50) & (data > -100))
print('___________________________')
print(data)

fig, ax = plt.subplots(figsize=(5,6), constrained_layout=True, facecolor='w', dpi=86)

# cmap = mpl.cm.get_cmap("viridis").copy() # cmap = plt.cm.viridis
# cmap.set_bad('#dddddd')

im = ax.imshow(data)
cb = fig.colorbar(im, shrink=.5)
cb.set_label('Bathymetry [m]')
plt.title('NOAA CoNED DEM')
plt.show()




