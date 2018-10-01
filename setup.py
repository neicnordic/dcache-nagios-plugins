'''
    Setup file for the package
'''

__author__ = "Petter Urkedal, Vincent Garonne"
__copyright__ = "Copyright 2018"
__credits__ = ["Petter Urkedal"]
__license__ = "Apache License, Version 2.0"
__version__ = "0.0.6"
__maintainer__ = "Vincent Garonne"
__email__ = "vgaronne@gmail.com"
__status__ = "Production"

from glob import glob
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='dcache-nagios-plugins',
    version=__version__,
    author="Petter Urkedal, Vincent Garonne",
    description="A collection of nagios plugins to monitor a dCache storage.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neicnordic/dcache-nagios-plugins/",
    license="Apache License, Version 2.0",
    data_files=[('nagios/plugins/libexec/dcache_nagios_plugins/',
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
