# This file is part of cpas.
#
# cpas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cpas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cpas.  If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (C) 2020 cpas team

"""
creation.py: A python script to create a cost surface from land cover, road and DEM datasets.
"""

import sys
from pathlib import Path
import resource
from timeit import default_timer as timer

# Imports
from . import tifs
import numpy as np

from .costsurface import lc, r, s, cs
from .config import CpasConfig

def main():
    start = timer()

    # read configuration file
    cfg = CpasConfig()
    cfg.read(sys.argv[1])

    #Processes

    # Get tiff attributes from land cover file, these will be used for other processes
    tiff_attributes = tifs.tiffHandle(cfg.landcover)
    tiff_attributes.readTiff(cfg.landcover)
    # Create in-memory driver with same attributes as the landcover input
    # This will be used as a template for resampling and rasterizing
    tiff_attributes.emptyTiff()

    # Extract land cover data 
    land_cover = tiff_attributes.data

    # Convert land cover to walking speeds
    land_cover_speeds = lc.lc_to_ws(land_cover, cfg.landcover_ws)

    # Convert roads to walking speeds
    roads = r.r_to_ws(cfg.roads, cfg.roads_ws, cfg.include_small_paths, tiff_attributes)

    # Combine roads and landcover walking speeds to make one surface
    ws_surface = r.backfill(land_cover_speeds, roads)

    # Create slope impact surface
    slope_impact = s.dem_to_slope_impact(cfg.dem, tiff_attributes,tempfile=str(cfg.outputbase/'resampleslope.tif'))

    # Include impact of slope in walking speeds surface
    ws_surface = ws_surface*(slope_impact/100)

    # Convert walking speed surface to a cost surface
    cost_surface = cs.ws_to_cs(ws_surface, cfg.child_impact, tiff_attributes.res)

    # Cost surface Output to tiff (water impassable)
    tiff_attributes.data = cost_surface
    tiff_attributes.writeTiff(cfg.costsurface)



    # Add water as passable
    land_cover = np.where(land_cover == 10, cfg.waterspeed, np.NaN)

    # convert water speed to time
    # 1 as children arnt slower than adults on motor boats... 
    land_cover = cs.ws_to_cs(land_cover, 1, tiff_attributes.res)

    # Add the water being passable to the original cost surface
    # != not equal  = nan
    # where cost surface is nan replace with new value to make water passable. 
    cost_surface = np.where(cost_surface != cost_surface, land_cover, cost_surface)

    # Output water cost surface to tiff
    tiff_attributes.data = cost_surface
    tiff_attributes.writeTiff(cfg.costsurface_water)


    end = timer()
    print(f'RAM usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)}')

    print(f'Time taken = {end-start}')

if __name__ == '__main__':
    main()
