import os
import re

from setuptools import setup


name = 'aws'
package = 'aws'
description = 'Utility to manage your Amazon Web Services and run Fabric against filtered set of EC2 instances.'
url = 'https://github.com/eofs/aws'
author = 'Tomi Pajunen'
author_email = 'tomi@madlab.fi'

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)

def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]

setup(name=name,
      version=get_version(package),
      description=description,
      url=url,
      author=author,
      author_email=author_email,
      license='MIT',
      packages=get_packages(package),
      zip_safe=False,
      requires=['boto', 'fabric'],
      entry_points={
          'console_scripts': ['aws=aws.main:main'],
      }
)