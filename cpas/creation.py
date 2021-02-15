"""
creation.py: A python script to create a cost surface from land cover, road and DEM datasets.
"""

import resource
from timeit import default_timer as timer

# Imports
import tifs
import numpy as np

from costsurface import lc, r, s, cs

start = timer()


#Inputs and Outputs

#path to files
p = '/home/s1891967/diss/Data/Input/'

# Landcover
lc_inp = p + 'UgandaLandCover/Uganda_Sentinel2_LULC2016.tif'
# Roads
r_inp = p + 'OSM_roads/AllRoads.shp'
# DEM
dem_inp = p + 'Uganda_SRTM30meters/Uganda_SRTM30meters.tif'

# Walking Speeds
lc_ws = p + 'Landcover_Costs.csv'
r_ws = p + 'Road_Costs.csv'

# Child Impact
child_impact = 0.78

# Paths
paths = True

# Water speed for water passable layer
waterspeed = 1.5

# Output
cs_out = '/home/s1891967/diss/Data/Output/cost_surface_200713.tif'

cs_water_out = '/home/s1891967/diss/Data/Output/cost_surface_water_200713.tif'


#Processes

# Get tiff attributes from land cover file, these will be used for other processes
tiff_attributes = tifs.tiffHandle(lc_inp)
tiff_attributes.readTiff(lc_inp)
# Create in-memory driver with same attributes as the landcover input
# This will be used as a template for resampling and rasterizing
tiff_attributes.emptyTiff()

# Extract land cover data 
land_cover = tiff_attributes.data

# Convert land cover to walking speeds
land_cover_speeds = lc.lc_to_ws(land_cover, lc_ws)

# Convert roads to walking speeds
roads = r.r_to_ws(r_inp, r_ws, paths, tiff_attributes)

# Combine roads and landcover walking speeds to make one surface
ws_surface = r.backfill(land_cover_speeds, roads)

# Create slope impact surface
slope_impact = s.dem_to_slope_impact(dem_inp, tiff_attributes)

# Include impact of slope in walking speeds surface
ws_surface = ws_surface*(slope_impact/100)

# Convert walking speed surface to a cost surface
cost_surface = cs.ws_to_cs(ws_surface, child_impact, tiff_attributes.res)

# Cost surface Output to tiff (water impassable)
tiff_attributes.data = cost_surface
tiff_attributes.writeTiff(cs_out)



# Add water as passable
land_cover = np.where(land_cover == 10, waterspeed, np.NaN)

# convert water speed to time
# 1 as children arnt slower than adults on motor boats... 
land_cover = cs.ws_to_cs(land_cover, 1, tiff_attributes.res)

# Add the water being passable to the original cost surface
# != not equal  = nan
# where cost surface is nan replace with new value to make water passable. 
cost_surface = np.where(cost_surface != cost_surface, land_cover, cost_surface)

# Output water cost surface to tiff
tiff_attributes.data = cost_surface
tiff_attributes.writeTiff(cs_water_out)


end = timer()
print(f'RAM usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)}')

print(f'Time taken = {end-start}')