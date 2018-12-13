#!/usr/bin/env python

import os
from distutils.util import convert_path
from setuptools import setup, find_packages

location = os.path.abspath(os.path.dirname(__file__))
with open('README.md') as readme:
    description = readme.read()
metadata = dict()
with open(convert_path('src/protobuf_simple_socket_rpc/version.py')) as metadata_file:
    exec(metadata_file.read(), metadata)


setup(
    name='protobuf_simple_socket_rpc',
    version=metadata['__version__'],

    description='Simple socket RPC implementation for Google Protobuf',
    long_description=description,

    url='https://github.com/exante/python-protobuf-simple-socket-rpc',
    author='EXANTE',
    author_email='',

    license='MIT',

    keywords='protubuf socket rpc',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    zip_safe=False,

    install_requires=[
        'protobuf'
    ]
)
