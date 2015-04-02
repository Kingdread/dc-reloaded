#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Various utility functions and classes for DC
"""
import ast
import os
import subprocess
import sys


def signed_value(val, bits):
    """
    Convert a "raw" value (which might be a two's complement) and a
    bitwidth and return the signed value, e.g.

    >>> signed_value(0b0101, 4)
    5
    >>> signed_value(0b1011, 4)
    -5
    """
    leftmost = val >> (bits - 1)
    if leftmost:
        # To get the two's complement of a number, we need to invert it
        # and add 1. The reverse is first subtracting 1 and then
        # inverting it to get the absolute of the number
        val = (~(val - 1)) & (2 ** bits - 1)
        # Because val is now the absolute of the number, we have to
        # make it negative again
        val = -1 * val
    return val


def number_of_digits(value, base=10):
    """
    Returns the number of digits the given number has in the given base
    >>> number_of_digits(999)
    3
    >>> number_of_digits(0b1010, 2)
    4
    """
    if not value:
        # Even 0 requires at least 1 digit
        return 1
    from math import log, floor
    return floor(log(value) / log(base)) + 1


def get_desktop_environment():
    """
    Returns the currently running desktop environment. Detection currently
    supports:
    - Mate (returns "mate")
    If detection failed, this function simply returns None
    """
    if sys.platform == "win32":
        # One moment of silence for the poor souls who use windows
        return

    # Try to detect Mate
    if "MATE_DESKTOP_SESSION_ID" in os.environ:
        return "mate"
    # MATE_DESKTOP_SESSION_ID is deprecated, so we might need a better
    # detection since we can't guarantee that we're not running Mate:
    command = [
        "dbus-send", "--print-reply", "--dest=org.freedesktop.DBus",
        "/org/freedesktop/DBus", "org.freedesktop.DBus.GetNameOwner",
        "string:org.mate.SessionManager",
    ]
    try:
        retval = subprocess.call(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
    except FileNotFoundError:
        pass
    else:
        if retval == 0:
            return "mate"


def fix_qt_icon_theme():
    """
    Attempts to fix the icon theme and the icon theme search path in desktop
    environments where Qt can't figure it out on its own. This is not
    guaranteed to work for every desktop environment and might be a simple
    no-op.
    """
    # Importing Qt here because we might use the module without a GUI. This way
    # it will only error when we actually use fix_qt_icon_theme
    from PyQt5 import QtGui

    env_name = get_desktop_environment()
    if env_name == "mate":
        # We can get the icon theme name via dconf
        command = ["dconf", "read", "/org/mate/desktop/interface/icon-theme"]
        try:
            icon_theme = subprocess.check_output(command)
        except FileNotFoundError:
            # Well, shit.
            pass
        except subprocess.CalledProcessError:
            pass
        else:
            icon_theme = icon_theme.decode("ascii", "ignore").strip()
            # looks like the output is enclosed in quotes
            icon_theme = ast.literal_eval(icon_theme)
            if not icon_theme:
                return
            paths = QtGui.QIcon.themeSearchPaths()
            paths.append("/usr/share/icons")
            QtGui.QIcon.setThemeSearchPaths(paths)
            QtGui.QIcon.setThemeName(icon_theme)


class IDict(dict):
    """
    Case-Insensitive dict. Keys can be everything that has a .lower()
    method.
    """
    def __init__(self, init=None, **kwargs):
        super().__init__()
        if init is not None:
            try:
                init = init.items()
            except AttributeError:
                pass
            for key, val in init:
                self[key] = val
        for key, val in kwargs.items():
            self[key] = val

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __delitem__(self, key):
        super().__delitem__(key.lower())

    def get(self, key, d):
        return super().get(key.lower(), d)

    def __contains__(self, key):
        return super().__contains__(key.lower())
