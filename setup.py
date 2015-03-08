#!/usr/bin/env python

"""
muspy_client setup script
"""

__author__ = 'David Poisl <david@poisl.at>'
__version__ = "1.0.0"

from setuptools import setup

setup(
    name='muspy_client',
    version='1.0.0a1',
    url='http://github.com/dpoisl/muspy_client',
    desscription='Client library for the API of muspy.com',
    long_description=open('README.md').read(),
    author='David Poisl',
    author_email='david@poisl.at',
    packages=['muspy_client'],
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Topic :: Software Development',
                 'Operating System :: OS Independent',
                 'License :: OSI Approved :: BSD License',
    ]
)
