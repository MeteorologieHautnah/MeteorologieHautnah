#!/usr/bin/env python
"""Helper functions

*author*: Johannes Röttenbacher
"""
import sys
import os


def read_command_line_args():
    """
    Read out command line arguments and save them to a dictionary. Expects arguments in the form key=value.

    Returns: dictionary with command line arguments as dict[key] = value

    """
    args = dict()
    for arg in sys.argv[1:]:
        if arg.count('=') == 1:
            key, value = arg.split('=')
            args[key] = value

    return args


def make_dir(folder: str) -> None:
    """
    Creates folder if it doesn't exist already.

    Args:
        folder: folder name or full path

    Returns: nothing, but creates a new folder if possible

    """
    try:
        os.makedirs(folder)
    except FileExistsError:
        pass
