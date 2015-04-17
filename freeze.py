#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
import sys
from cx_Freeze import setup, Executable


def get_version():
    try:
        version = subprocess.check_output(["git", "describe", "--abbrev=0"])
        version = version.lstrip("v")
        return version.strip().decode("utf-8")
    except Exception as e:
        print(e, file=sys.stderr)
        print("Couldn't get git version, falling back to setup.py version",
              file=sys.stderr)

    import re
    version_re = r"""version *= *(["'])(.+)\1"""
    with open("setup.py", "r") as setup_py:
        content = setup_py.read()
        match = re.search(version_re, content)
        if match:
            return match.group(2).lstrip("v")

    print("No setup.py version found", file=sys.stderr)
    return "undefined"

base = "Win32GUI" if sys.platform == "win32" else None

build_exe_options = {
    "excludes": ["tkinter"],
    "zip_includes": [
        # Tuple source/dest file, otherwise they end up in wrong directories
        ("dc/interface/static/short_help.html",
         "dc/interface/static/short_help.html"),
    ],
}

bdist_msi_options = {
    "add_to_path": False,
    "upgrade_code": "{ce110df4-67c4-43f4-bfa6-fcfd1ac11378}",
}

executables = [
    Executable(
        "scripts/dc-reloaded",
        base=base,
        icon="resource-files/cpu.ico",
        shortcutName="DC reloaded",
        shortcutDir="ProgramMenuFolder",
    ),
]

setup(
    name="DC reloaded",
    description="DC reloaded",
    version=get_version(),
    executables=executables,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
)
