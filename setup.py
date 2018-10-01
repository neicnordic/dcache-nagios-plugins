'''
    Setup file for the package
'''

__author__ = "Petter Urkedal, Vincent Garonne"
__copyright__ = "Copyright 2018"
__credits__ = ["Petter Urkedal"]
__license__ = "Apache License, Version 2.0"
__version__ = "0.0.1"
__maintainer__ = "Vincent Garonne"
__email__ = "vgaronne@gmail.com"
__status__ = "Production"

import os
import sys

from glob import glob
from setuptools import setup, find_packages

print find_packages()

setup(
    name='dcache-nagios-plugins',
    version=__version__,
    author="Petter Urkedal, Vincent Garonne",
    description="A collection of nagios plugins to monitor a dCache storage.",
    license="Apache License, Version 2.0",
    scripts=glob("bin/*"),
    data_files=[(os.path.join(sys.prefix,
                              'libexec',
                              'dcache_nagios_plugins'),
                              glob("libexec/*"))],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Environment :: No Input/Output (Daemon)'],
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),)
