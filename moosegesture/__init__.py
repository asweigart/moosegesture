"""
MooseGesture - A mouse gestures recognition library.
By Al Sweigart al@coffeeghost.net
http://coffeeghost.net/2011/05/09/moosegesture-python-mouse-gestures-module

Usage:
    import moosegesture
    gesture = moosegesture.getGesture(points)

Where "points" is a list of x, y coordinate tuples, e.g. [(100, 200), (1234, 5678), ...]
getGesture returns a list of string for the recognized mouse gesture. The strings
correspond to the 8 cardinal and diagonal directions:

    'UL' (up-left), 'U' (up), 'UR' (up-right)
    'L' (left), 'R' (right)
    'DL' (down-left), 'D' (down), 'DR' (down-right)

Second usage:
    strokes  = ['D', 'L', 'R']
    gestures = [['D', 'L', 'D'], ['D', 'R', 'UR']]
    gesture = moosegesture.findClosestMatchingGesture(strokes, gestures)

    gesture == ['D', 'L', 'D']

Where "strokes" is a list of the directional integers that are returned from
getGesture(). This returns the closest resembling gesture from the list of
gestures that is passed to the function.

The optional "tolerance" parameter can ensure that the "closest" identified
gesture isn't too different.


Explanation of the nomenclature in this module:
    A "point" is a 2D tuple of x, y values. These values can be ints or floats,
    MooseGesture supports both.

    A "point pair" is a point and its immediately subsequent point, i.e. two
    points that are next to each other.

    A "segment" is two or more ordered points forming a series of lines.

    A "stroke" is a segment going in a single direction (one of the 8 cardinal or
    diagonal directions: up, upright, left, etc.)

    A "gesture" is one or more strokes in a specific pattern, e.g. up then right
    then down then left.


"""

__version__ = '1.0.2'

import doctest

from math import sqrt

# This is the minimum distance the mouse must travel (in pixels) before a
# segment will be considered for stroke interpretation.
_MIN_STROKE_LEN = 60

DOWNLEFT = 'DL'
DOWN = 'D'
DOWNRIGHT = 'DR'
LEFT = 'L'
RIGHT = 'R'
UPLEFT = 'UL'
UP = 'U'
UPRIGHT = 'UR'

def getGesture(points):
    """
    Returns a gesture as a list of directions, i.e. ['U', 'DL'] for
    the down-left-right gesture.

    The `points` parameter is a list of (x, y) tuples of points that make up
    the user's mouse gesture.
    """
    return _identifyStrokes(points)[0]


def getSegments(points):
    """
    Returns a list of tuples of integers. The tuples are the start and end
    indexes of the points that make up a consistent stroke.
    """
    return _identifyStrokes(points)[1]


def getGestureAndSegments(points):
    """
    Returns a list of tuples. The first item in the tuple is the directional
    integer, and the second item is a tuple of integers for the start and end
    indexes of the points that make up the stroke.
    """
    strokes, strokeSegments = _identifyStrokes(points)
    return list(zip(strokes, strokeSegments))


def findClosestMatchingGesture(strokes, gestureList, maxDifference=None):
    """
    Returns the gesture(s) in `gestureList` that closest matches the gesture in
    `strokes`. The `maxDifference` is how many differences there can be and still
    be considered a match.
    """
    if len(gestureList) == 0:
        return None

    #gestureList = [list(frozenset(tuple(gesture))) for gesture in gestureList] # make a unique list
    gestureList = frozenset([tuple(gesture) for gesture in gestureList])
    distances = {}
    for g in gestureList:
        levDist = levenshteinDistance(strokes, g)
        if maxDifference is None or levDist <= maxDifference:
            distances.setdefault(levDist, [])
            distances[levDist].append(g)

    if not distances:
        return None # No matching gestures are within the tolerance of maxDifference.

    return tuple(distances[min(distances.keys())])


def levenshteinDistance(s1, s2):
    """
    Returns the Levenshtein Distance between two strings, `s1` and `s2` as an
    integer.

    http://en.wikipedia.org/wiki/Levenshtein_distance
    The Levenshtein Distance (aka edit distance) is how many changes (i.e.
    insertions, deletions, substitutions) have to be made to convert one
    string into another.

    For example, the Levenshtein distance between "kitten" and "sitting" is
    3, since the following three edits change one into the other, and there
    is no way to do it with fewer than three edits:
      kitten -> sitten -> sittin -> sitting
    """
    singleLetterMapping = {DOWNLEFT: '1', DOWN:'2', DOWNRIGHT:'3',
                           LEFT:'4', RIGHT:'6',
                           UPLEFT:'7', UP:'8', UPRIGHT:'9'}

    len1 = len([singleLetterMapping[letter] for letter in s1])
    len2 = len([singleLetterMapping[letter] for letter in s2])

    matrix = list(range(len1 + 1)) * (len2 + 1)
    for i in range(len2 + 1):
        matrix[i] = list(range(i, i + len1 + 1))
    for i in range(len2):
        for j in range(len1):
            if s1[j] == s2[i]:
                matrix[i+1][j+1] = min(matrix[i+1][j] + 1, matrix[i][j+1] + 1, matrix[i][j])
            else:
                matrix[i+1][j+1] = min(matrix[i+1][j] + 1, matrix[i][j+1] + 1, matrix[i][j] + 1)
    return matrix[len2][len1]


def _identifyStrokes(points):
    strokes = []
    strokeSegments = []

    # calculate lengths between each sequential points
    distances = []
    for i in range(len(points)-1):
        distances.append( _distance(points[i], points[i+1]) )

    # keeps getting points until we go past the min. segment length
    #startSegPoint = 0
    #while startSegPoint < len(points)-1:
    for startSegPoint in range(len(points)-1):
        segmentDist = 0
        curDir = None
        consistent = True
        direction = None
        for curSegPoint in range(startSegPoint, len(points)-1):
            segmentDist += distances[curSegPoint]
            if segmentDist >= _MIN_STROKE_LEN:
                # check if all points are going the same direction.
                for i in range(startSegPoint, curSegPoint):
                    direction = _getDirection(points[i], points[i+1])
                    if curDir is None:
                        curDir = direction
                    elif direction != curDir:
                        consistent = False
                        break
                break
        if not consistent:
            continue
        elif (direction is not None and ( (not len(strokes)) or (len(strokes) and strokes[-1] != direction) )):
            strokes.append(direction)
            strokeSegments.append( [startSegPoint, curSegPoint] )
        elif len(strokeSegments):
            # update and lengthen the latest stroke since this stroke is being lengthened.
            strokeSegments[-1][1] = curSegPoint
    return strokes, strokeSegments

def _getDirection(coord1, coord2):
    """
    Return the direction the line formed by the (x, y)
    points in `coord1` and `coord2`.
    """
    x1, y1 = coord1
    x2, y2 = coord2

    if x1 == x2 and y1 == y2:
        return None # two coordinates are the same.
    elif x1 == x2 and y1 > y2:
        return UP
    elif x1 == x2 and y1 < y2:
        return DOWN
    elif x1 > x2 and y1 == y2:
        return LEFT
    elif x1 < x2 and y1 == y2:
        return RIGHT

    slope = float(y2 - y1) / float(x2 - x1)

    # Figure out which quadrant the line is going in, and then
    # determine the closest direction by calculating the slope
    if x2 > x1 and y2 < y1: # up right quadrant
        if slope > -0.4142:
            return RIGHT # slope is between 0 and 22.5 degrees
        elif slope < -2.4142:
            return UP # slope is between 67.5 and 90 degrees
        else:
            return UPRIGHT # slope is between 22.5 and 67.5 degrees
    elif x2 > x1 and y2 > y1: # down right quadrant
        if slope > 2.4142:
            return DOWN
        elif slope < 0.4142:
            return RIGHT
        else:
            return DOWNRIGHT
    elif x2 < x1 and y2 < y1: # up left quadrant
        if slope < 0.4142:
            return LEFT
        elif slope > 2.4142:
            return UP
        else:
            return UPLEFT
    elif x2 < x1 and y2 > y1: # down left quadrant
        if slope < -2.4142:
            return DOWN
        elif slope > -0.4142:
            return LEFT
        else:
            return DOWNLEFT

def _distance(coord1, coord2):
    """
    Return the distance between two points, `coord1` and `coord2`. These
    parameters are assumed to be (x, y) tuples.
    """
    xdist = coord1[0] - coord2[0]
    ydist = coord1[1] - coord2[1]
    return sqrt(xdist*xdist + ydist*ydist)
