"""
MooseGesture Test application
Al Sweigart al@coffeeghost.net
http://coffeeghost.net/2011/05/09/moosegesture-python-mouse-gestures-module

Run the app and then draw by dragging the mouse. When you release the mouse
button, the gesture you drew will be identified.


This script requires the MooseGesture library, which you can download from here:
http://coffeeghost.net/moosegesture.py

And also requires Pygame:
http://pygame.org

Copyright 2011, BSD-license.
"""

import pygame, random, sys
from pygame.locals import *
import moosegesture

# setup constants
WINDOWWIDTH = 600
WINDOWHEIGHT = 600
FPS = 40

TEXTCOLOR = (255, 255, 255) # white
BACKGROUNDCOLOR = (0, 0, 0)# black
POINTSCOLOR = (255, 0, 0) # red
LINECOLOR = (255, 165, 0) # orange
CARDINALCOLOR = (0, 255, 0) # green
DIAGONALCOLOR = (0, 0, 255) # blue

# set up pygame, the window, and the mouse cursor
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Mouse Gesture Test')

points = []
mouseDown = False
font = pygame.font.SysFont(None, 24)
strokeText = ''

while True: # main loop
    for event in pygame.event.get():
        # handle all pygame events
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

        if event.type == MOUSEBUTTONDOWN:
            # on mouse down, erase the previous line and start drawing a new one
            mouseDown = True
            if len(points) > 2:
                startx, starty = points[0][0], points[0][1]
                for i in range(len(points)):
                    points[i] = (points[i][0] - startx, points[i][1] - starty)
            points = []
            storkeText = ''

        if event.type == MOUSEBUTTONUP:
            # try to identify the gesture when the mouse dragging stops
            mouseDown = False
            strokes = moosegesture.getGesture(points)
            segments = moosegesture.getSegments(points)
            strokeText = moosegesture.getGestureStr(strokes)
            textobj = font.render(strokeText, 1, (255,255,255))
            textrect = textobj.get_rect()
            textrect.topleft = (10, WINDOWHEIGHT - 30)

        if event.type == MOUSEMOTION and mouseDown:
            # draw the line if the mouse is dragging
            points.append( (event.pos[0], event.pos[1]) )


    # Draw the window.
    windowSurface.fill(BACKGROUNDCOLOR)

    if strokeText:
        # draw the identified strokes of the last line
        windowSurface.blit(textobj, textrect)

    # draw points
    for x, y in points:
        pygame.draw.circle(windowSurface, POINTSCOLOR, (x, y), 2)

    if mouseDown:
        # draw strokes as unidentified while dragging the mouse
        if len(points) > 1:
            pygame.draw.lines(windowSurface, LINECOLOR, False, points)
    else:
        # draw the identified strokes
        segNum = 0
        curColor = LINECOLOR
        for p in range(len(points)-1):

            if segNum < len(segments) and segments[segNum][0] == p:
                # start of new stroke
                if strokes[segNum] in [2, 4, 6, 8]:
                    curColor = CARDINALCOLOR
                elif strokes[segNum] in [1, 3, 7, 9]:
                    curColor = DIAGONALCOLOR
            pygame.draw.line(windowSurface, curColor, points[p], points[p+1])

            if segNum < len(segments) and segments[segNum][1] == p:
                # end of a stroke
                curColor = LINECOLOR
                segNum += 1

    pygame.display.update()
    mainClock.tick(FPS)