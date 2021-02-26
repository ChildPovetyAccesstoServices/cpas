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

# Least Cost path utilising scipy
# http://tretherington.blogspot.com/2017/01/least-cost-modelling-with-python-using.html
# https://scikit-image.org/docs/0.7.0/api/skimage.graph.mcp.html

# Import packages
import numpy as np
from skimage import graph
import geopandas as gpd
import random
import tifs
import cs_test


def least_cost(cs, startCell, endCell):
    """Find route and cost from start cell to end cell using cost surface"""

    # Make any values below one equal to no data
    np.place(cs, cs < 1, -9999)

    # to find path and cost
    route, cost = graph.mcp.route_through_array(
        cs, startCell, endCell, fully_connected=True, geometric=True)

    return route, cost


def service_area(cs, startCells):
    """create a grid of access to services"""

    # From the cost-surface create a 'landscape graph' object which can then be
    # analysed using least-cost modelling
    lg = graph.MCP_Geometric(cs, sampling=None)

    # Calculate the least-cost distance from the start cell to all other cells
    # [0] is returning the cumulative costs rather than the traceback
    lcd = lg.find_costs(starts=startCells)[0]

    return lcd


def validate_starts(locs, cs):
    """validate locations are within extent of cost surface"""
    health = cs_test.clean_invalid_loc(locs, cs)

    start_cells = []

    # validate locations are on passable cells
    for index, row in health.iterrows():
        # convert health care lat lon to pixel ref
        xInds = int(((row.geometry.x - cs.xOrigin)) / cs.pixelWidth)
        yInds = int((cs.yOrigin - row.geometry.y) / -cs.pixelHeight)

        vals = cs.data[yInds, xInds]
        # find value for location and where not null
        if vals == vals:
            start_cells.append((yInds, xInds))
        else:
            # move to neighbouring cell is passable
            sq = [(i, j) for i in range(yInds - 1, yInds + 2)
                  for j in range(xInds - 1, xInds + 2)]
            gd_sq = [c for c in sq if cs.data[c] == cs.data[c]]
            if len(gd_sq) > 0:
                new_cell = random.choice(gd_sq)
                start_cells.append(new_cell)

    return start_cells


if __name__ == "__main__":

    # import both cost surfaces
    # cost surface
    cs_fn = '/home/s1891967/diss/Data/Output/cost_surface_200713.tif'
    cs = tifs.tiffHandle(cs_fn)
    cs.readTiff(cs_fn)

    # water passable cost surface
    csw_fn = '/home/s1891967/diss/Data/Output/cost_surface_water_200713.tif'
    csw = tifs.tiffHandle(csw_fn)
    csw.readTiff(csw_fn)

    # import health care locations
    health_inp = '/home/s1891967/diss/Data/Input/Health/UgandaClinics.shp'
    health = gpd.read_file(health_inp)

    # validata health service locations are valid to use with cost surface
    start_cells = validate_starts(health, cs)

    # find costs algorithm does not deal with np.NaN so change these
    # to -9999 in cost surface any negative values are ignored
    cs.data = np.where(cs.data != cs.data, -9999, cs.data)

    # calculate the costs for each square in the grid
    cs.sa = service_area(cs.data, start_cells)

    # where impassable infinity is returned as cost
    # change these to no data for output
    np.place(cs.sa, np.isinf(cs.sa), np.NaN)

    # repeat the above with water passable cost surface
    start_cells = validate_starts(health, csw)
    csw.data = np.where(csw.data != csw.data, -9999, csw.data)
    csw.sa = service_area(csw.data, start_cells)
    np.place(csw.sa, np.isinf(csw.sa), np.NaN)

    # bring both access layers together for output
    cs.data = np.where(cs.sa == cs.sa, cs.sa, csw.sa)

    print('Writing tiff')
    cs.writeTiff('/home/s1891967/diss/Data/Output/ServiceArea.tif')
