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
import sys
import rioxarray
import xarray
import numpy
from skimage import graph
import geopandas
import random
from .config import CpasConfig


def service_area(cs, startCells):
    """create a grid of access to services"""

    # From the cost-surface create a 'landscape graph' object which can then be
    # analysed using least-cost modelling
    lg = graph.MCP_Geometric(cs.values, sampling=None)

    lcd = xarray.zeros_like(cs, dtype=numpy.float32)

    # Calculate the least-cost distance from the start cell to all other cells
    # [0] is returning the cumulative costs rather than the traceback
    lcd.values = lg.find_costs(starts=startCells)[0]

    return lcd


def find_location_cells(health_services, cs):
    """find cell indices of health service locations

    Parameters
    ----------
    health_services: geopandas data frame containing locations
    cs: costsurface
    """

    start_cells = []

    # loop over all health service locations
    longs = cs.get_index('x')
    lats = cs.get_index('y')

    for location in health_services['geometry']:
        idx_i = longs.get_loc(location.x, method='nearest')
        idx_j = lats.get_loc(location.y, method='nearest')

        if cs[0, idx_j, idx_i].isnull():
            # if the cell is not valid check neighbouring cells
            alternatives = []
            for j in range(idx_j - 1, idx_j + 2):
                for i in range(idx_i - 1, idx_i + 2):
                    if not cs[0, j, i].isnull():
                        alternatives.append((0, j, i))
            if len(alternatives) > 0:
                # select a random neighbour
                start_cells.append(random.choice(alternatives))
        else:
            start_cells.append((0, idx_j, idx_i))

    return start_cells


def compute_cost_path(csname, hname):
    """compute cost paths

    Parameters
    ----------
    csname: name of input costsurface file
    hname: name of file containing health service locations
    """

    # import both cost surfaces
    # cost surface
    costsurface = rioxarray.open_rasterio(csname, masked=True)

    # # import health care locations
    health = geopandas.read_file(
        hname,
        bbox=costsurface.rio.bounds())

    # select health service locations that are valid to use with cost surface
    start_cells = find_location_cells(health, costsurface)

    # find costs algorithm does not deal with np.NaN so change these
    # to -9999 in cost surface any negative values are ignored
    costsurface = costsurface.fillna(-9999)
    # cs.data = np.where(cs.data != cs.data, -9999, cs.data)

    # # calculate the costs for each square in the grid
    costs = service_area(costsurface, start_cells)

    costs = xarray.where(numpy.isfinite(costs), costs, numpy.nan)

    return costs


def main():
    # read configuration
    cfg = CpasConfig()
    cfg.read(sys.argv[1])

    # repeat the above with water passable cost surface
    cp = compute_cost_path(cfg.costsurface, cfg.health_care)
    cw = compute_cost_path(cfg.costsurface_water, cfg.health_care)

    # bring both access layers together for output
    cp = xarray.where(cp.isnull(), cw, cp)

    cp.rio.to_raster(cfg.cost_path)


if __name__ == "__main__":
    main()
