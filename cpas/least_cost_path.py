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


def find_location_cells(destinations, cs):
    """find cell indices of destination locations

    Parameters
    ----------
    destinations: geopandas data frame containing locations
    cs: costsurface
    """

    start_cells = []
    status = []

    # loop over all destination locations
    longs = cs.get_index('x')
    lats = cs.get_index('y')

    for location in destinations['geometry']:
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
                status.append('m')
            else:
                status.append('i')
        else:
            start_cells.append((0, idx_j, idx_i))
            status.append('v')

    return start_cells, status


def compute_cost_path(csname, dname, invalid_loc):
    """compute cost paths

    Parameters
    ----------
    csname: name of input costsurface file
    dname: name of file containing destination locations
    invalid_loc: name of file for storing invalid locations
    """

    # import both cost surfaces
    # cost surface
    costsurface = rioxarray.open_rasterio(csname, masked=True)

    # import destination locations
    destinations = geopandas.read_file(
        dname,
        bbox=costsurface.rio.bounds())

    # select destination locations that are valid to use with cost surface
    start_cells, status = find_location_cells(destinations, costsurface)
    destinations['status'] = status
    count = destinations.status.value_counts()
    if 'v' in count:
        print(f"found {count['v']} valid locations")
    if 'm' in count:
        print(f"moved {count['m']} locations")
    if 'i' in count:
        print(f"found {count['i']} invalid locations")
    with open(invalid_loc, 'w') as invalid_out:
        for row in destinations[(destinations['status'] == 'i')].itertuples():
            invalid_out.write(f'{row.Long},{row.Lat},"{row.Facility_n}"\n')

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
    cp = compute_cost_path(cfg.costsurface, cfg.destinations, cfg.invalid_loc)
    cw = compute_cost_path(cfg.costsurface_water, cfg.destinations,
                           cfg.invalid_loc_water)

    # bring both access layers together for output
    cp = xarray.where(cp.isnull(), cw, cp)

    cp.rio.to_raster(cfg.cost_path)


if __name__ == "__main__":
    main()
