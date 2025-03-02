#-------------------------------------------------------------------------------
# Name:        KenKenPuzzle
# Purpose:     A KenKen maker
#
# Author:      Dustin Gehm
#
# Created:     21/11/2017
# Copyright:   (c) Dustin Gehm 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import KenKen;
import logging;
import pygame;
import random;
import sys;

ScriptName: str = sys.argv[0].removesuffix(".py");

logger: logging.Logger = logging.Logger(ScriptName);

WindowSize: tuple[int, int] = (1000, 600);

# On-screen instructions
Instructions: list[str] = [
    "S -> Saves KenKen puzzle to black and white image",
    "K -> Saves KenKen answer key to color image",
    "L -> Prompts for new size and seed",
];

instructions_just: int = len(max(Instructions, key=len));


def query_kenken_props() -> tuple[int, int]:
    # Ask for a size and seed
    grid_size: int = 3;
    seed: int = random.randrange(sys.maxsize);

    temp_input: str = input("Enter a size for the KenKen(default is 3): ");

    if temp_input:
        try:
            grid_size = int(temp_input.strip());

            if grid_size < 3:
                grid_size = 3;
            elif grid_size > 9:
                grid_size = 9;
        except ValueError as e:
            logger.error(f"{temp_input} is not a valid integer, defaulting to size of 3");

            grid_size = 3;

    temp_input: str = input("Enter a seed for the KenKen(default is random): ");

    if temp_input:
        try:
            seed = int(temp_input.strip());
        except ValueError as e:
            logger.error(f"{temp_input} is not a valid integer, defaulting to random seed");

            seed = random.randrange(sys.maxsize);

    return grid_size, seed;


def main() -> None:
    k_size, k_seed = query_kenken_props();
    print("KenKen key ", k_seed);

    kk: KenKen.KenKen = KenKen.KenKen(k_size, k_seed);
    kk.generate();

    pygame.display.init();
    pygame.font.init();
    pygame.display.set_caption("KenKen Generator");

    screen: pygame.Surface = pygame.display.set_mode(WindowSize);
    big_font: pygame.font.Font = pygame.font.SysFont("Arial", 30);
    small_font: pygame.font.Font = pygame.font.SysFont("Arial", 15);
    done: bool = False;

    while not done:
        screen.fill((255, 255, 255));

        events: list[pygame.event.Event] = pygame.event.get();

        for e in events:
            if e.type == pygame.QUIT:
                done = True;
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    done = True;
                elif e.key == pygame.K_l:
                    k_size, k_seed = query_kenken_props();
                    print("new KenKen key ", k_seed);

                    kk = KenKen.KenKen(k_size, k_seed);
                    kk.generate();
                elif e.key == pygame.K_s:
                    #save kenken to png file
                    surf = pygame.Surface((kk.size * 100, kk.size * 100));
                    surf.fill((255, 255, 255));
                    kk.mark_dirty();
                    kk.draw(surf, 0, 0, big_font, small_font);
                    pygame.image.save(surf, f"KenKen_sz{str(kk.size)}_{str(k_seed)}.png");
                    kk.mark_dirty();
                    print("KenKen saved to image file");
                elif e.key == pygame.K_k:
                    #save kenken answer key to png file
                    surf = pygame.Surface((kk.size * 100, kk.size * 100));
                    surf.fill((255, 255, 255));
                    kk.mark_dirty();
                    kk.draw(surf, 0, 0, big_font, small_font, answers=True);
                    pygame.image.save(surf, f"KenKen_sz{str(kk.size)}_{str(k_seed)}_answers.png");
                    kk.mark_dirty();
                    print("KenKen answer key saved to image file");

        kk.draw(screen, 0, 0, big_font, small_font, answers = True);

        for i, info in enumerate([
            f"Verified: {kk.verify_all()}",
            f"Seed: {k_seed}",
                ]):
            screen.blit(small_font.render(info, True, (0, 0, 0)), (WindowSize[0] - small_font.size(info)[0] - 10, small_font.get_height() * i));

        for i, line in enumerate(Instructions):
            line = line.ljust(instructions_just);

            screen.blit(small_font.render(line, True, (0, 0, 0)), (WindowSize[0] - small_font.size(line)[0] - 10, (small_font.get_height() * 1.1 * (i + 5))));

        pygame.display.flip();

    pygame.font.quit();
    pygame.display.quit();

if __name__ == '__main__':
    main();
