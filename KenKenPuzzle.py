#-------------------------------------------------------------------------------
# Name:        KenKenPuzzle
# Purpose:     A KenKen maker
#
# Author:      Dustin
#
# Created:     21/11/2017
# Copyright:   (c) Dustin 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import sys;
import random;
import pygame;
import KenKen;

def queryNewKenken():
    #ask for a size and seed
    gridSize = 0;
    kkSeed = 0;
    dataIn = input("Enter \"Size, Seed\" for new KenKen: ").split(',');

    try:
        gridSize = int(dataIn[0].strip());
    except:
        gridSize = 3;

    try:
        kkSeed = int(dataIn[1].strip());
    except:
        kkSeed = random.randrange(sys.maxsize);

    if gridSize < 3:
        gridSize = 3;
    elif gridSize > 9:
        gridSize = 9;

    return (gridSize, kkSeed);

##    kk = KenKen.KenKen(kenkenSize, rngSeed);
##    print("new KenKen key ", rngSeed);
##    kk.generate();

def main():
    kenkenSize = 3;
    rngSeed = 0;

    kenkenSize, rngSeed = queryNewKenken();
##    rngSeed = 423885109;  #test
##    rngSeed = 883658446;  #test2
##    rngSeed = 310154206;  #size 5, index out of range error
##    rngSeed = 1339593442; #size 5, 2x2 cage
##    rngSeed = 517824060;  #size 5, zigzag cage
##    rngSeed = 2065751865; #quick case
    print("KenKen key ", rngSeed);

    windim = (800, 600);

    kk = KenKen.KenKen(kenkenSize, rngSeed);
    kk.generate();

    pygame.display.init();
    pygame.font.init();
    pygame.display.set_caption("Esc -> Quit, S -> save, L -> load");
    screen = pygame.display.set_mode(windim);
    bigFont = pygame.font.SysFont("Arial", 30);
    smallFont = pygame.font.SysFont("Arial", 15);
    done = False;

    while not done:
        screen.fill((255, 255, 255));

        events = pygame.event.get();

        for e in events:
            if e.type == pygame.QUIT:
                done = True;
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    done = True;
                elif e.key == pygame.K_l:
                    kenkenSize, rngSeed = queryNewKenken();
                    print("new KenKen key ", rngSeed);

                    kk = KenKen.KenKen(kenkenSize, rngSeed);
                    kk.generate();
                elif e.key == pygame.K_s:
                    #save kenken to png file
                    surf = pygame.Surface((kk.size * 100, kk.size * 100));
                    surf.fill((255, 255, 255));
                    kk.markDirty();
                    kk.draw(surf, 0, 0, bigFont, smallFont);
                    pygame.image.save(surf, "KenKenS" + str(kk.size) + "_" + str(rngSeed) + ".png");
                    kk.markDirty();
                    print("KenKen saved to image file");

        kk.draw(screen, 0, 0, bigFont, smallFont, answers = True);
        screen.blit(smallFont.render(str(kk.verify()), False, (0, 0, 0)), (windim[0] - smallFont.size(str(kk.verify()))[0], 0));
        screen.blit(smallFont.render(str(rngSeed), False, (0, 0, 0)), (windim[0] - smallFont.size(str(rngSeed))[0], smallFont.get_height()));

        pygame.display.flip();

    pygame.font.quit();
    pygame.display.quit();

if __name__ == '__main__':
    main();
