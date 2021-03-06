
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

from configobj import ConfigObj
from validate import Validator
from pathlib import Path

# the defaults
defaultCfgStr = """
[inputs]
# base path to input files, all inputs are relative to this directory
inputbase = string

[[landcover]]
# name of tiff file containing landcover
name = string
# a csv file containing the landcover type to speed map
speeds = string
# the name of the column containing the land cover types
landcover_type_column = string(default=Code)
# the name of the column containing the speeds
speed_column = string(default=Walking Speed (km/h))

[[roads]]
# name of shape file containing roads
name = string
#  a csv file containing the roads type to speed map
speeds = string
# the name of the column containing the road types
road_type_column = string(default=Feature_Class)
# the name of the column containing the speeds
speed_column = string(default=Walking_Speed)

[[dem]]
# name of tiff file containing DEM
name = string

[[walking_speeds]]
# factor applied to walking speed when walking with children
child_impact = float(default=0.78)
# Water speed for water passable layer
waterspeed = float(default=1.5)

[[destinations]]
# destination locations such as health care centres
name = string
# whether to include small paths
include_small_paths = boolean(default=True)
# tag describing name of destination
tag = string(default=Facility_n)

[outputs]
# base path for output files
outputbase = string
costsurface = string
costsurface_water = string
cost_path = string
invalid_loc = string(default=invalid_loc.csv)
invalid_loc_water = string(default=invalid_loc_water.csv)

# by default the maximum road speed is taken for each pixel. You can speed up
# the road rasterisation process and reduce memory usage by setting this value
# to False. All roads are processed in no particular order thus some cells
# might end up with a slower speed.
take_max_road_speed = bool(default=True)

[plotting]
# map projection for plotting
epsg_code = string(default=4326)
"""

cpasDefaults = ConfigObj(defaultCfgStr.split('\n'),
                         list_values=False, _inspec=True)
validator = Validator()


class CpasConfig:
    def __init__(self):
        self._cfg = ConfigObj(configspec=cpasDefaults)
        self._cfg.validate(validator)

    def read(self, fname):
        """read and parse configuration file"""

        fname = Path(fname)

        if not fname.is_file():
            msg = f'no such configuration file {fname}'
            raise RuntimeError(msg)

        self._cfg.filename = str(fname)
        self._cfg.reload()
        if not self._cfg.validate(validator):
            msg = f'Could not read config file {fname}'
            raise RuntimeError(msg)

        self._landcover_cfg = None
        self._roads_cfg = None
        self._destinations_cfg = None

    @property
    def cfg(self):
        return self._cfg

    @property
    def landcover_cfg(self):
        if self._landcover_cfg is None:
            self._landcover_cfg = {}
            for f in ['name', 'speeds']:
                self._landcover_cfg[f] = \
                    self.inputbase / Path(self.cfg['inputs']['landcover'][f])
            for k in ['landcover_type_column', 'speed_column']:
                self._landcover_cfg[k] = self.cfg['inputs']['landcover'][k]
        return self._landcover_cfg

    @property
    def destinations_cfg(self):
        if self._destinations_cfg is None:
            self._destinations_cfg = {}
            self._destinations_cfg['name'] = \
                self.inputbase /\
                Path(self.cfg['inputs']['destinations']['name'])
            for k in ['include_small_paths', 'tag']:
                self._destinations_cfg[k] = \
                    self.cfg['inputs']['destinations'][k]
        return self._destinations_cfg

    @property
    def roads_cfg(self):
        if self._roads_cfg is None:
            self._roads_cfg = {}
            for f in ['name', 'speeds']:
                self._roads_cfg[f] = \
                    self.inputbase / Path(self.cfg['inputs']['roads'][f])
            for k in ['road_type_column', 'speed_column']:
                self._roads_cfg[k] = self.cfg['inputs']['roads'][k]
        return self._roads_cfg

    @property
    def inputbase(self):
        return Path(self.cfg['inputs']['inputbase'])

    @property
    def landcover(self):
        return str(self.landcover_cfg['name'])

    @property
    def roads(self):
        return str(self.roads_cfg['name'])

    @property
    def dem(self):
        return str(self.inputbase / Path(self.cfg['inputs']['dem']['name']))

    @property
    def landcover_ws(self):
        return str(self.landcover_cfg['speeds'])

    @property
    def roads_ws(self):
        return str(self.roads_cfg['speeds'])

    @property
    def destinations(self):
        return str(self.destinations_cfg['name'])

    @property
    def child_impact(self):
        return self.cfg['inputs']['walking_speeds']['child_impact']

    @property
    def include_small_paths(self):
        return self.destinations_cfg['include_small_paths']

    @property
    def waterspeed(self):
        return self.cfg['inputs']['walking_speeds']['waterspeed']

    @property
    def outputbase(self):
        base = Path(self.cfg['outputs']['outputbase'])
        if not base.exists():
            base.mkdir(parents=True)
        return base

    @property
    def costsurface(self):
        return str(self.outputbase / Path(self.cfg['outputs']['costsurface']))

    @property
    def costsurface_water(self):
        return str(self.outputbase / Path(
            self.cfg['outputs']['costsurface_water']))

    @property
    def cost_path(self):
        return str(self.outputbase / Path(self.cfg['outputs']['cost_path']))

    @property
    def invalid_loc(self):
        return str(self.outputbase / Path(self.cfg['outputs']['invalid_loc']))

    @property
    def invalid_loc_water(self):
        return str(self.outputbase / Path(
            self.cfg['outputs']['invalid_loc_water']))

    @property
    def take_max_road_speed(self):
        return self.cfg['outputs']['take_max_road_speed']

    @property
    def epsg_code(self):
        return self.cfg['plotting']['epsg_code']


if __name__ == '__main__':
    import sys
    from pprint import pprint

    cfg = CpasConfig()

    if len(sys.argv) > 1:
        cfg.read(Path(sys.argv[1]))

    pprint(cfg.cfg.dict())

    for c in ['landcover', 'roads', 'dem', 'landcover_ws', 'roads_ws',
              'child_impact', 'include_small_paths', 'waterspeed',
              'costsurface', 'costsurface_water', 'invalid_loc',
              'invalid_loc_water', 'take_max_road_speed', 'epsg_code']:
        print(c, getattr(cfg, c))

    pprint(cfg.landcover_cfg)
    pprint(cfg.roads_cfg)
    pprint(cfg.destinations_cfg)
