#!/usr/bin/python3

import os
from setuptools import setup

def read_file(name):
    name = os.path.join(os.path.dirname(__file__), name)
    with open(name) as input_file:
        return input_file.read()

setup(
    name="dc-reloaded",
    version="0.1b0",
    description="A small CPU simulator",
    long_description=read_file("README.md"),
    author="Daniel Schadt",
    author_email="daniel@kingdread.de",
    url="https://github.com/Kingdread/dc-reloaded/",
    license="GPL",
    packages=[
        "dc",
        "dc.interface",
    ],
    include_package_data=True,
    scripts=[
        "scripts/dc-reloaded",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Assembly",
        "Topic :: Education",
    ],
)
