#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'beautifulsoup4',
    'mock',
    'numpy',
    'pandas',
    'python-dateutil',
    'pytz',
    'six',
    'requests',
    'TA-lib',
    'zipline',
]

test_requirements = [
    'mock',
]

setup(
    name='stockbot',
    version='0.2.0',
    description='Stock market analysis library written in Python.',
    long_description=readme + '\n\n' + history,
    author='Chris Pappalardo',
    author_email='cpappala@yahoo.com',
    url='https://github.com/ChrisPappalardo/stockbot',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license='CC BY-NC-ND 4.0',
    zip_safe=False,
    keywords='stockbot',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
