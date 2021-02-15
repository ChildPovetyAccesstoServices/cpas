cpas
====
child poverty access to services code

Installation
------------
On an Ubuntu system you can install the required packages using
```
apt install gdal python3-fuzzywuzzy python3-gdal python3-numpy python3-pandas
```

You can install the code into a virtual environment if you wish to:
```
# create virtual environment
python3 -m venv /PATH/TO/VENV --system-site-packages
# activate it
. /PATH/TO/VENV/bin/activate
# install code
python setup.py install
# and run it
cpas-create CFG
```
On an Ubuntu system you can install the required packages using
```
apt install gdal python3-fuzzywuzzy python3-gdal python3-numpy python3-pandas
```

You can also run the program directly without having to install it first:
```
python3 -m cpas.creation CFG
```
