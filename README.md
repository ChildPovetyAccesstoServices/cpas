cpas
====
child poverty access to services code

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
cpas-create CFG
cpas-path CFG
```

You can also run the programs directly without having to install them first:
```
python3 -m cpas.creation CFG
python3 -m cpas.least_cost_path CFG
```
