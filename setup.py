#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    print('Skipping md->rst conversion for long_description')
    long_description = 'Error converting Markdown from git repo'

if len(long_description) < 100:
    print("\n***\n***\nWARNING: %s\n***\n***\n" % long_description)

setup(
    name='insteonplm',
    version='0.8.1',
    author='David McNett',
    author_email='nugget@macnugget.org',
    url='https://github.com/nugget/python-insteonplm',
    license="LICENSE",
    packages=find_packages(),
    scripts=[],
    description='Python API for controlling Insteon PowerLinc Modems',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'pyserial==3.2.0',
        'pyserial-asyncio',
        'async_timeout'
    ],
    entry_points={
        'console_scripts': [ 'insteonplm_monitor = insteonplm.tools:monitor', ]
    }
)
