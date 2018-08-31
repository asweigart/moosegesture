============
MooseGesture
============

A mouse gesture recognition module for Python 2 and 3.

This module is fed a series of XY coordinates (which can come from the mouse or another source) and can recognize when the mouse is moving in one of the eight cardinal/diagonal directions.

These mouse movements can be combined to form "mouse gestures" to perform different commands.

Installation
============

    ``pip install moosegesture``

Quickstart Guide
================

Pass a path as sequence of (x, y) tuples to `getGesture()`, which will return a list of directions that the path takes. These are the up, down, left, right, and diagonal directions represented by the following strings:

    ``'U', 'D', 'L', 'R'``

    ``'UL', 'UR', 'DL', 'DR'``

They are stored in the following constants:

    ``UP, DOWN, LEFT, RIGHT``

    ``UPLEFT, UPRIGHT, DOWNLEFT, DOWNRIGHT``

Example usage:

    >>> import moosegesture
    >>> moosegesture.getGesture([(332, 385), (332, 287), (332, 175), (330, 69), (324, 13), (322, 0)])
    ['U']

MooseGesture can also find the closest matching gesture in a list of gestures, using Levenshtein edit distance:

    >>> path  = ['D', 'L', 'R']
    >>> gestures = [['D', 'L', 'D'], ['D', 'R', 'UR']]
    >>> moosegesture.findClosestMatchingGesture(path, gestures)
    ['D', 'L', 'D']

The same direction will never appear consecutively, i.e. there will never be a "right-left-left" gesture, only "right-left".

Demo Programs
=============

The repo at https://github.com/asweigart/moosegesture contains a `tests/demoGestureApp.py` which uses Pygame to display a small window. You can draw gestures in this window by dragging the mouse, and the recognized gesture will appear at the bottom.

The `simongesture.py` game is a Simon game that make uses of `moosegesture`. It requires Pygame to play.