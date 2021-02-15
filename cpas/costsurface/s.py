"""
s.py: A python script containing functions needed to make DEM into speed impact for inclusion in cost surface.

Inspiration from:
https://jgomezdans.github.io/gdal_notes/reprojection.html
https://gis.stackexchange.com/questions/234022/resampling-a-raster-from-python-without-using-gdalwarp
"""

# Imports
import sys
sys.path.append('/home/s1891967/diss/code/Diss/')

import numpy as np
from osgeo import gdal, gdalconst
# Enable GDAL/OGR exceptions (enabling error messages)
gdal.UseExceptions()

from cpas.tifs import *

def resamplefunc(inputfile, ta):
    """Resample tiff based on gdal object read from tiff

    Parameters
    ----------
    inputfile  : str
        The file location of the tiff to be resampled
    ta : obj
        The gdal object holding tiff attributes

    Returns
    -------
    ta.dst_ds
        Resampled gdal object
    """

    # Gather input file information
    inp = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
    inputProj = inp.GetProjection()
    inputTrans = inp.GetGeoTransform()

    # Undertake resampling 
    # Use Bilinear as most suitable for datatype and usage
    gdal.ReprojectImage(inp, ta.dst_ds, inputProj, ta.proj, gdalconst.GRA_Bilinear)

    # GDAL object returned by function
    return ta.dst_ds

def calculate_gradient(inputDEM, outputstring):
    """Function to calculate slope from DEM

    Parameters
    ----------
    inputDEM  : gdal object
        Resampled DEM in-memory object
    outputstring : str
        A file location to output the slope tif too
    """
    gdal.DEMProcessing(outputstring, inputDEM, 'slope', scale=111120)
    # TODO: see if we can get as percent output rather than converting later...

def toosteep(arr):
    """Make nodata values and where steepness is over 45 degrees into NaN so not calculated

    Parameters
    ----------
    arr  : np.array
        Array of gradient values

    Returns
    -------
    arr2
        Array of passable gradient values
    """
    arr1 = np.where(arr > 45, np.NaN, arr)
    arr2 = np.where(arr == -9999, np.NaN, arr1)
    return arr2

def gradtoslope(arr):
    """Convert gradients (degrees) to slope (%)

    Parameters
    ----------
    arr  : np.array
        Array of gradient values

    Returns
    -------
    arr3
        Array of slope values
    """
    arr1 = np.radians(arr) # convert from degrees to radians
    arr2 = np.tan(arr1) # calculate tan of radians
    arr3 = arr2 * 100 # calculate slope %
    return arr3



def slopespeed(a):
    """Function to calculate equation from Irmischer and Clarke (2018). 
    This models walking speed based on slope.

    Parameters
    ----------
    a  : np.array
        Array slope values

    Returns
    -------
    0.11 + np.exp(((-(a + 5)**2)/(2*30**2)))
        Result of equation
    """
    return 0.11 + np.exp(((-(a + 5)**2)/(2*30**2)))


def slopeimpact(b):
    """
    Function to calculate the impact of slope on walking speed. 

    Finds mean of speed for both upwards and downwards of a slope (%).
    This is then calculated as a percentage of the speed for 0 slope (i.e. flat)

        Parameters
    ----------
    b  : np.array
        Array slope values

    Returns
    -------
    (((0.5*(slopespeed(+b)+slopespeed(-b))/slopespeed(0)) * 100))
        Result of equation
    """
    return (((0.5*(slopespeed(+b)+slopespeed(-b))/slopespeed(0)) * 100))


def dem_to_slope_impact(DEM, ta):

    """Function to calculate slope impact from DEM

    Parameters
    ----------
    DEM  : str
        The file location of the DEM file
    ta : gdal object
        A gdal object of tiff attributes

    Returns
    -------
    slope_arr
        Array of slope impact
    """

    tempstring = 'resampleslope.tif'
    
    # Resample
    rs_dem = resamplefunc(DEM, ta)

    # Calculate Gradient (degrees)
    calculate_gradient(rs_dem, tempstring)

    # Read slope tiff in 
    a = tiffHandle(tempstring)
    a.readTiff(tempstring)

    # Make over 45 degree slope no data
    slope_arr = toosteep(a.data)

    # Convert to Slope (%)
    slope_arr = gradtoslope(slope_arr)

    # Calculate slope impact (%)
    slope_arr = slopeimpact(slope_arr)

    return slope_arr


if __name__ == '__main__':

    # Input DEM layer
    SRTM30 = '/home/s1891967/diss/Data/Input/Uganda_SRTM30meters/Uganda_SRTM30meters.tif'

    # Input Land Cover layer (for reference in resampling)
    LC = '/home/s1891967/diss/Data/Input/UgandaLandCover/Uganda_Sentinel2_LULC2016.tif'

    # Output
    out = '/home/s1891967/diss/Data/Output/slope_impact.tif'
    
    ta = tiffHandle(LC)
    ta.readTiff(LC)
    ta.emptyTiff()
    
    ta.data = dem_to_slope_impact(SRTM30, ta)

    ta.writeTiff(out)
    










