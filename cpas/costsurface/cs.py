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
cs.py: A python script containing functions to convert walking speed into cost surfaces
"""

# Imports


def ws_to_cs(ws_surface, child_impact, res):
    """Convert walking speeds to a cost surface

    Parameters
    ----------
    ws_surface  : np.array
        The walking speeds surface
    child_impact : flt
        Percentage by which adult walking speeds are reduced to child walking speeds

    Returns
    -------
    cs
        Cost surface
    """

    # reduce by child impact
    arr = ws_surface*child_impact

    # TODO: how to do this for public transport? some roads will only be walking others not...  

    # convert from km/hour to m/s
    arr = arr*1000/3600

    # convert to time (seconds) from speeds
    # TODO: should this be the surface resolution rather than 20m - no as measures in m/s
    # might be good to convert to res converted into m
    # speed = distance/time
    cs = 20/arr

    return cs





