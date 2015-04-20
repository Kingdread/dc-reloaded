#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from cx_Freeze import setup, Executable
from setupcommon import setupdata

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
    executables=executables,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    **setupdata
)
