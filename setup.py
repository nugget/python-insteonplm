#!/usr/bin/env python3
"""Setup for insteonplm module."""
from setuptools import setup, find_packages


def readme():
    """Return README file as a string."""
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='insteonplm',
    version='0.15.4',
    author='David McNett',
    author_email='nugget@macnugget.org',
    url='https://github.com/nugget/python-insteonplm',
    license="MIT License",
    packages=find_packages(),
    scripts=[],
    description='Python API for controlling Insteon PowerLinc Modems',
    long_description=readme(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'pyserial==3.2.0',
        'pyserial-asyncio',
        'async_timeout',
        'aiohttp'
    ],
    entry_points={
        'console_scripts': ['insteonplm_monitor = insteonplm.tools:monitor',
                            'insteonplm_interactive = '
                            'insteonplm.tools:interactive']
    }
)
