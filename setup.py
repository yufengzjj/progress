#!/usr/bin/env python

from setuptools import setup

import progress

setup(
    name='progress',
    version=progress.__version__,
    description='Easy to use progress bars',
    long_description=open('README.rst').read(),
    author='yufeng.zjj',
    author_email='yufeng.zjj@gmail.com',
    url='http://github.com/yufengzjj/progress/',
    license='ISC',
    packages=['progress'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
