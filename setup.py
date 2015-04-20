#!/usr/bin/python3
from setupcommon import setupdata
from setuptools import setup

setup(
    packages=[
        "dc",
        "dc.interface",
    ],
    include_package_data=True,
    scripts=[
        "scripts/dc-reloaded",
    ],
    **setupdata
)
