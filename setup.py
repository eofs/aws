import os
import re

from setuptools import setup, find_packages

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

setup(name=name,
      version=get_version(package),
      description=description,
      url=url,
      author=author,
      author_email=author_email,
      license='BSD',
      packages=find_packages(),
      zip_safe=False,
      install_requires=['boto', 'fabric>=1.6', 'prettytable>=0.7'],
      entry_points={
          'console_scripts': ['aws=aws.main:main'],
      },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Clustering',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
)