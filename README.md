cpas
====
child poverty access to services code

Depending on the size of area under consideration this program can use up a lot of memory.

Installation
------------
On an Ubuntu system you can install the required packages using
```
apt install gdal python3-fuzzywuzzy python3-gdal python3-numpy \
     python3-pandas python3-rioxarray python3-fiona python3-geopandas \
	 python3-xarray pyton3-skimage
```

You can install the code into a virtual environment if you wish to:
```
# create virtual environment
python3 -m venv /PATH/TO/VENV --system-site-packages
# activate it
. /PATH/TO/VENV/bin/activate
# you might need to install pyproj
# pip install -U pyproj
# install code
python setup.py install
# and run it
cpas-compute CFG
cpas-path CFG
cpas-plot CFG
```

You can also run the programs directly without having to install them first:
```
python3 -m cpas.compute CFG
python3 -m cpas.least_cost_path CFG
python3 -m cpas.plot CFG
```

The plotting program has various command line options:
```
usage: plot.py [-h] [-s GEOTIFF] [-l] [-o FILE] CFG

positional arguments:
  CFG                   name of configuration file

optional arguments:
  -h, --help            show this help message and exit
  -s GEOTIFF, --speed-surface GEOTIFF
                        load speed surface from GEOTIFF
  -l, --show-health-services
                        show locations of helth services
  -o FILE, --output FILE
                        save figure to FILE
```


Installation into a Conda Environment
-------------------------------------
Once a python 3.8 evironment has been created and activated install the dependencies using
```
conda install fuzzywuzzy numpy pandas  scikit-image xarray configobj
conda install rioxarray
conda install fiona
pip install geopandas
```
Then install cpas as above.
