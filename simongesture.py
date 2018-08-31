# Simon Gesture (a Simon clone with mouse gestures)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Creative Commons BY-NC-SA 3.0 US

# Requires the moosegesture module: pip install moosegesture

# Background music from http://www.freesound.org/people/ERH/sounds/30192/

__version__ = '1.0.0'

import random, sys, pygame, moosegesture
from pygame.locals import MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN, KEYDOWN, KEYUP, K_m, K_ESCAPE, QUIT
from moosegesture import UP, UPRIGHT, RIGHT, DOWNRIGHT, DOWN,DOWNLEFT, LEFT, UPLEFT

FPS = 30 # frames per second. Increase to speed up the game.
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FLASHSPEED = 500 # in milliseconds
FLASHDELAY = 200 # in milliseconds
TIMEOUT = 4 # seconds before game over if no button is pushed.

FADESPEED = 10 # larger number is faster fade speed

GESTURE_LEN = 60 # how long the game's gestures are

#                R    G    B
WHITE        = (255, 255, 255)
BLACK        = (  0,   0,   0)
LIGHTGRAY    = (185, 185, 185)
DARKGRAY     = ( 40,  40,  40)
RED          = (255,   0,   0)
BLUE         = (  0,   0, 255)

BGCOLOR = WHITE
DOTCOLOR = DARKGRAY
ARROWCOLOR = BLUE

DOTRADIUS = 10 # size of dot
MAXGESTURES = 100 # max number of gestures (no way the player will be able to memorize this many)

# directional constants (made to be the same as moosegesture's
DIRECTIONS = (UP, UPRIGHT, RIGHT, DOWNRIGHT, DOWN, DOWNLEFT, LEFT, UPLEFT)

# the blue hint arrow that shows what the most recent gesture the player made is.
ARROWSIZE = 20
ARROWWIDTH = 2
HALFARROWSIZE = int(ARROWSIZE / 2)

def main():
    global FPSCLOCK, WINDOWSURF, BASICFONT, BEEP1, BEEP2, BEEP3, BEEP4

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    WINDOWSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Simon Gesture')

    BASICFONT = pygame.font.Font('freesansbold.ttf', 16)

    # set up surf and rect for instructional text
    infoSurf = BASICFONT.render('Drag the mouse to match the directional pattern. Press M to toggle music.', 1, LIGHTGRAY)
    infoRect = infoSurf.get_rect()
    infoRect.topleft = (10, WINDOWHEIGHT - 25)

    musicLoaded = True
    try:
        # This mp3 can be downloaded from http://www.freesound.org/people/ERH/sounds/30192/
        pygame.mixer.music.load('simonbackground.mp3')
        pygame.mixer.music.play(-1, 0.0)
    except pygame.error:
        musicLoaded = False

    musicPlaying = True
    newGame = True

    while True: # main game loop
        if newGame:
            # Initialize some variables
            score = 0
            # when False, the pattern is playing. when True, waiting for the player to click a colored button:
            waitingForInput = False

            # sequence must be calculated in advance so we know the dimensions, and thus the start point
            seq = []
            for i in range(MAXGESTURES):
                seq.append(addToSequence(seq))
            mouseDown = False
            mousex, mousey = None, None
            playerMouseMovement = [] # a list of (x, y) tuples of mouse positions the player has moved
            mouseJustReleased = False
            newGame = False

        # basic drawing stuff
        WINDOWSURF.fill(BGCOLOR)

        scoreSurf = BASICFONT.render('Score: ' + str(score), 1, LIGHTGRAY)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (WINDOWWIDTH - 100, 10)
        WINDOWSURF.blit(scoreSurf, scoreRect)

        WINDOWSURF.blit(infoSurf, infoRect)

        checkForQuit()
        mousex, mousey = None, None # stores where the last mouse motion event occurred.
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouseDown = False
                mouseJustReleased = True
            elif event.type == MOUSEBUTTONDOWN:
                mouseDown = True
            elif event.type == KEYDOWN and event.key == K_m:
                 # toggle music
                musicPlaying = not musicPlaying
                if musicLoaded:
                    if musicPlaying:
                        pygame.mixer.music.play(-1, 0.0)
                    else:
                        pygame.mixer.music.stop()

        if mouseJustReleased:
            mouseJustReleased = False
            # see if the gesture matches
            gestures = moosegesture.getGesture(playerMouseMovement)
            if gestures != seq[:score+1]:
                # gesture didn't match
                drawGameOver()
                newGame = True

            waitingForInput = False
            score += 1
            continue

        if not waitingForInput:
            # show the animation sequence
            animateSequence(seq, score+1)
            waitingForInput = True
            playerMouseMovement = []
        else:
            # let the player enter their response
            if mousex != None and mousey != None and mouseDown:
                playerMouseMovement.append( (mousex, mousey) )

            if len(playerMouseMovement) > 1:
                pygame.draw.lines(WINDOWSURF, BLACK, False, playerMouseMovement)
                gestures = moosegesture.getGesture(playerMouseMovement)
                if len(gestures) > 0:
                    drawArrow(int(WINDOWWIDTH / 2) - HALFARROWSIZE, WINDOWHEIGHT - 80, gestures[-1])
                if gestures != seq[:len(gestures)] or len(gestures) > score + 1:
                    drawGameOver()
                    newGame = True
                    continue

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawArrow(x, y, direction):
    if direction is None:
        pygame.draw.rect(WINDOWSURF, BGCOLOR, (x, y, ARROWSIZE, ARROWSIZE))
        return

    lines = []

    # draw the main line of the arrow
    if direction in (UP, DOWN):
        lines.append( ((HALFARROWSIZE, 0), (HALFARROWSIZE, ARROWSIZE)) )
    elif direction in (LEFT, RIGHT):
        lines.append( ((0, HALFARROWSIZE), (ARROWSIZE, HALFARROWSIZE)) )
    elif direction in (UPLEFT, DOWNRIGHT):
        lines.append( ((0, 0), (ARROWSIZE, ARROWSIZE)) )
    elif direction in (UPRIGHT, DOWNLEFT):
        lines.append( ((ARROWSIZE, 0), (0, ARROWSIZE)) )

    # draw the two angled short lines
    if direction == UP:
        lines.append( ((HALFARROWSIZE, 0), (0, HALFARROWSIZE)) )
        lines.append( ((HALFARROWSIZE, 0), (ARROWSIZE, HALFARROWSIZE)) )
    elif direction == DOWN:
        lines.append( ((HALFARROWSIZE, ARROWSIZE), (0, HALFARROWSIZE)) )
        lines.append( ((HALFARROWSIZE, ARROWSIZE), (ARROWSIZE, HALFARROWSIZE)) )
    elif direction == LEFT:
        lines.append( ((0, HALFARROWSIZE), (HALFARROWSIZE, 0)) )
        lines.append( ((0, HALFARROWSIZE), (HALFARROWSIZE, ARROWSIZE)) )
    elif direction == RIGHT:
        lines.append( ((ARROWSIZE, HALFARROWSIZE), (HALFARROWSIZE, 0)) )
        lines.append( ((ARROWSIZE, HALFARROWSIZE), (HALFARROWSIZE, ARROWSIZE)) )
    elif direction == UPRIGHT:
        lines.append( ((ARROWSIZE, 0), (HALFARROWSIZE, 0)) )
        lines.append( ((ARROWSIZE, 0), (ARROWSIZE, HALFARROWSIZE)) )
    elif direction == UPLEFT:
        lines.append( ((0, 0), (0, HALFARROWSIZE)) )
        lines.append( ((0, 0), (HALFARROWSIZE, 0)) )
    elif direction == DOWNRIGHT:
        lines.append( ((ARROWSIZE, ARROWSIZE), (HALFARROWSIZE, ARROWSIZE)) )
        lines.append( ((ARROWSIZE, ARROWSIZE), (ARROWSIZE, HALFARROWSIZE)) )
    elif direction == DOWNLEFT:
        lines.append( ((0, ARROWSIZE), (0, HALFARROWSIZE)) )
        lines.append( ((0, ARROWSIZE), (HALFARROWSIZE, ARROWSIZE, )) )

    for line in lines:
        pygame.draw.line(WINDOWSURF, ARROWCOLOR, (x + line[0][0], y + line[0][1]), (x + line[1][0], y + line[1][1]), ARROWWIDTH)

def drawGameOver():
    # draw the big red X that means game over.
    pygame.draw.line(WINDOWSURF, RED, (50, 50), (WINDOWWIDTH - 50, WINDOWHEIGHT - 50), 40)
    pygame.draw.line(WINDOWSURF, RED, (WINDOWWIDTH - 50, 50), (50, WINDOWHEIGHT - 50), 40)
    pygame.display.update()
    pygame.time.wait(2500)
    waitForPlayerToReleaseMouse()
    WINDOWSURF.fill(BGCOLOR)
    pygame.display.update()


def waitForPlayerToReleaseMouse():
    while True:
        # Wait for player to release the mouse button
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
        if pygame.mouse.get_pressed() == (0, 0, 0):
            return
        pygame.display.update()

def addToSequence(seq):
    # randomly select a direction that can be added to the sequence.
    if seq == []:
        return random.choice(DIRECTIONS)

    dirs = list(DIRECTIONS)
    dirs.remove(seq[-1]) # don't repeat the last step

    while True:
        randomdir = random.choice(dirs)
        width, height, firstx, firsty = getDimensionsOfSequence(seq + [randomdir])
        if width > int(WINDOWWIDTH / 2) or height > int(WINDOWHEIGHT / 2):
            # don't allow directions that go too far from the center of the window
            dirs.remove(randomdir)
        else:
            return randomdir


def animateSequence(seq, steps):
    width, height, firstx, firsty = getDimensionsOfSequence(seq)
    xmargin = int((WINDOWWIDTH - width) / 2)
    ymargin = int((WINDOWHEIGHT - height) / 2)

    startx = firstx + xmargin
    starty = firsty + ymargin
    fade(startx, starty, 'in')
    for direction in seq[:steps]:
        if pygame.event.get(QUIT) != []:
            terminate()
        diffx = 0
        diffy = 0
        if direction in (UP, UPRIGHT, UPLEFT):
            diffy = -GESTURE_LEN
        elif direction in (DOWN, DOWNRIGHT, DOWNLEFT):
            diffy = GESTURE_LEN
        if direction in (RIGHT, UPRIGHT, DOWNRIGHT):
            diffx = GESTURE_LEN
        elif direction in (LEFT, UPLEFT, DOWNLEFT):
            diffx = -GESTURE_LEN

        for progress in range(0, 100, 5):
            progressx = startx + int(diffx * (progress / 100.0))
            progressy = starty + int(diffy * (progress / 100.0))
            pygame.draw.circle(WINDOWSURF, DOTCOLOR, (progressx, progressy), DOTRADIUS)
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            pygame.draw.circle(WINDOWSURF, BGCOLOR, (progressx, progressy), DOTRADIUS)
        startx += diffx
        starty += diffy
    fade(startx, starty, 'out')
    waitForPlayerToReleaseMouse()

def fade(x, y, fade):
    # dot fade animation. 'fade' can be 'in' or 'out' to fade in or fade out.
    if fade == 'in':
        start, end, step = 255, 40, -FADESPEED
    elif fade == 'out':
        start, end, step = 40, 255, FADESPEED*3

    for i in range(start, end, step):
        col = pygame.Color(i, i, i)
        pygame.draw.circle(WINDOWSURF, col, (x, y), DOTRADIUS)
        pygame.display.update()
        FPSCLOCK.tick(FPS)



def getDimensionsOfSequence(seq):
    # get the total area the sequence will expand over (we do this so we can make sure the animation doesn't go past the edge of the window)

    # For example, [UP, DOWN] will have a dimension of 0 x 1. Whereas [UP, UP, DOWN] will be 0 x 2. [UP, DOWN, UP, DOWN, UP, DOWN, LEFT] will be 1 x 1
    maxWidth = 0
    maxHeight = 0
    startx = 0
    starty = 0

    x = 0
    y = 0

    for i in seq:
        if i in (UP, UPRIGHT, UPLEFT):
            y -= 1
        if i in (DOWN, DOWNRIGHT, DOWNLEFT):
            y += 1
        if i in (UPRIGHT, RIGHT, DOWNRIGHT):
            x += 1
        if i in (UPLEFT, LEFT, DOWNLEFT):
            x -= 1

        if x < 0:
            maxWidth += abs(x)
            startx += abs(x)
            x = 0
        if y < 0:
            maxHeight += abs(y)
            starty += abs(y)
            y = 0

        if x > maxWidth:
            maxWidth = x
        if y > maxHeight:
            maxHeight = y

    return (maxWidth * GESTURE_LEN, maxHeight * GESTURE_LEN, startx * GESTURE_LEN, starty * GESTURE_LEN)

def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


if __name__ == '__main__':
    main()
