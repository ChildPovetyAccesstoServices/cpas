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

from .config import CpasConfig
from matplotlib import pyplot
import cartopy
import geopandas
import rioxarray
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', metavar='CFG',
                        help="name of configuration file")
    parser.add_argument('-s', '--speed-surface', metavar='GEOTIFF',
                        help="load speed surface from GEOTIFF")
    parser.add_argument('-l', '--show-destination-locations', default=False,
                        action="store_true",
                        help="show locations of destinations")
    parser.add_argument('-o', '--output', metavar='FILE',
                        help="save figure to FILE")
    args = parser.parse_args()

    cfg = CpasConfig()
    cfg.read(args.config)

    if cfg.epsg_code == "4326":
        crs = cartopy.crs.PlateCarree()
    else:
        crs = cartopy.crs.epsg(cfg.epsg_code)
    ax = pyplot.axes(projection=crs)

    if args.speed_surface is not None:
        data = rioxarray.open_rasterio(args.speed_surface, masked=True)
        cmap = pyplot.get_cmap('viridis')
        data[0, :, :].plot.imshow(ax=ax, cmap=cmap)
    else:
        # convert seconds into hours
        data = rioxarray.open_rasterio(cfg.cost_path, masked=True) / 3600
        cmap = pyplot.get_cmap('viridis_r')
        data[0, :, :].plot.imshow(ax=ax, cmap=cmap, vmin=0, vmax=10)

    ax.set_title('')
    ax.gridlines(draw_labels=True)
    ax.add_feature(cartopy.feature.BORDERS)

    if args.show_destination_locations:
        destinations = geopandas.read_file(
            cfg.destinations,
            bbox=data.rio.bounds()).to_crs(epsg=cfg.epsg_code)
        destinations.plot(ax=ax, marker='o', markersize=5, color='black')

    if args.output is not None:
        pyplot.savefig(args.output)
    else:
        pyplot.show()


if __name__ == '__main__':
    main()
