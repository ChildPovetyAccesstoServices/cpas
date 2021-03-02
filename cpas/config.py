
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
# name of tiff file containing landcover
landcover = string
# name of shape file containing roads
roads = string
# name of tiff file containing DEM
dem = string
# walking speed
landcover_ws = string
roads_ws = string
# health care locations
health_care = string

# factor applied to walking speed when walking with children
child_impact = float(default=0.78)

# whether to include small paths
include_small_paths = boolean(default=True)

# Water speed for water passable layer
waterspeed = float(default=1.5)


[outputs]
# base path for output files
outputbase = string
costsurface = string
costsurface_water = string
cost_path = string
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

    @property
    def cfg(self):
        return self._cfg

    @property
    def inputbase(self):
        return Path(self.cfg['inputs']['inputbase'])

    @property
    def landcover(self):
        return str(self.inputbase / Path(self.cfg['inputs']['landcover']))

    @property
    def roads(self):
        return str(self.inputbase / Path(self.cfg['inputs']['roads']))

    @property
    def dem(self):
        return str(self.inputbase / Path(self.cfg['inputs']['dem']))

    @property
    def landcover_ws(self):
        return str(self.inputbase / Path(self.cfg['inputs']['landcover_ws']))

    @property
    def roads_ws(self):
        return str(self.inputbase / Path(self.cfg['inputs']['roads_ws']))

    @property
    def health_care(self):
        return str(self.inputbase / Path(self.cfg['inputs']['health_care']))

    @property
    def child_impact(self):
        return self.cfg['inputs']['child_impact']

    @property
    def include_small_paths(self):
        return self.cfg['inputs']['include_small_paths']

    @property
    def waterspeed(self):
        return self.cfg['inputs']['waterspeed']

    @property
    def outputbase(self):
        return Path(self.cfg['outputs']['outputbase'])

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


if __name__ == '__main__':
    import sys
    from pprint import pprint

    cfg = CpasConfig()

    if len(sys.argv) > 1:
        cfg.read(Path(sys.argv[1]))

    pprint(cfg.cfg.dict())

    for c in ['landcover', 'roads', 'dem', 'landcover_ws', 'roads_ws',
              'child_impact', 'include_small_paths', 'waterspeed',
              'costsurface', 'costsurface_water']:
        print(c, getattr(cfg, c))
