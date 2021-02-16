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
lc.py: A python script containing function to convert land cover to walking speeds

Inspiration from: 
https://stackoverflow.com/questions/34321025/replace-values-in-numpy-2d-array-based-on-pandas-dataframe
"""

import sys
sys.path.append('/home/s1891967/diss/code/Diss/')

# Imports
import pandas as pd
import numpy as np

from cpas import tifs


def lc_to_ws(arr, ws):
    """Converts a landcover surface to walking speed surface

    Parameters
    ----------
    arr : np.array
        An array of land cover codes
    ws : str
        The file location of the csv file for landcover walking speeds

    Returns
    -------
    arr
        An array of walking speeds
    """

    # Read as csv file as dataframe
    costs = pd.read_csv(ws)
    # Extract codes and walking speeds
    oldval = np.array(costs['Code'])
    newval = np.array(costs['Walking Speed (km/h)'])
    # TODO: Could look at other ways of doing this less reliant upon spreadsheet structure
    # TODO: Possibility for including other transport modes

    # Change data type of land cover data from int to float
    arr = arr.astype(np.float64)

    # Replace land cover values with respective walking speeds
    mask = np.in1d(arr,oldval)
    idx = np.searchsorted(oldval,arr.ravel()[mask])
    arr.ravel()[mask] = newval[idx]
    mask.reshape(arr.shape)
    # TODO: Work out exactly what this does?

    # Replace 0.0 with null values
    arr = np.where(arr == 0.0, np.NaN, arr)

    return arr

if __name__ == '__main__':
    # If script is run directly will take input land cover tif and convert to walking speeds tiff

    #path to files
    p = '/home/s1891967/diss/Data/Input/'
    # Landcover
    lc_inp = p + 'UgandaLandCover/Uganda_Sentinel2_LULC2016.tif'
    # Walking Speeds
    lc_ws = p + 'Landcover_Costs.csv'

    # Output
    ws_out = '/home/s1891967/diss/Data/Output/lc_ws_surface.tif'

    # Read land cover tiff
    landcover = tifs.tiffHandle(lc_inp)
    landcover.readTiff(lc_inp)

    print(landcover)

    # Convert land cover to walking speeds
    landcover.data = lc_to_ws(landcover.data, lc_ws)

    print(landcover.data)

    # Write walking speeds tiff out
    landcover.writeTiff(ws_out)
