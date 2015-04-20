#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import os
import subprocess
import sys


def get_version():
    try:
        version = subprocess.check_output(["git", "describe", "--abbrev=0"])
        version = version.decode("utf-8").lstrip("v")
        return version.strip()
    except Exception as e:
        print(e, file=sys.stderr)
        print("Couldn't get git version",
              file=sys.stderr)
    # Don't raise an error, it's nicer to return None so we can use a
    # ternary if
    return None


def read_file(name):
    name = os.path.join(os.path.dirname(__file__), name)
    with open(name) as input_file:
        return input_file.read()


__version__ = (0, 1, 0)

setupdata = {
    "name": "DC reloaded",
    "description": "A small CPU simulator",
    "version": get_version() or ".".join(__version__),
    "long_description": read_file("README.md"),
    "author": "Daniel Schadt",
    "author_email": "daniel@kingdread.de",
    "url": "https://github.com/Kingdread/dc-reloaded",
    "license": "GPL",
    "classifiers": [
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Assembly",
        "Topic :: Education",
    ],
}
