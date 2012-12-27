#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='servo',
    version='1.0',
    description="",
    author="Filipp Lepalaan",
    author_email='filipp@mcare.fi',
    url='',
    packages=find_packages(),
    package_data={'servo': ['static/*.*', 'templates/*.*']},
    scripts=['manage.py'],
)
