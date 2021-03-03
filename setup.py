#!/usr/bin/env python3

from setuptools import setup

setup(name='cpas',
      python_requires='>=3',
      install_requires=[],
      version='0.1',
      description="child poverty access to services",
      url='https://github.com/ChildPovetyAccesstoServices/cpas',
      packages=['cpas', 'cpas.costsurface'],
      entry_points={
          'console_scripts': [
              'cpas-create = cpas.compute:main',
              'cpas-path = cpas.least_cost_path:main',
          ],
      },
      )
