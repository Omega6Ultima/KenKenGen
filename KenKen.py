#-------------------------------------------------------------------------------
# Name:        KenKen
# Purpose:     Encapsulate all the functions needed to interact with
#               mathematical Ken Ken puzzles
#
# Author:      Dustin Gehm
#
# Created:     07/11/2017
# Copyright:   (c) Dustin Gehm 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import pygame;
import random;
import sys;
import time;
from typing import override


class KenKen:
    Colors: list[tuple[int, int, int]] = [];
    TwoValOperators: list[str] = ['+', '-', '*', '/'];
    ThreeValOperators: list[str] = ['+', '*'];
    ProgressMessages: list[str] = [
        "Reticulating splines",
        "Calibrating calibration",
        "I lost count :(",
        "Sequencing number fabrication",
        "Taking a small break",
        "Getting more coffee",
        "Shoot! I dropped one",
        "Are numbers even real?",
        "Isn't python great?",
        "Loading bar says 10 more seconds"
    ];

    class Cage:
        def __init__(self, squares: list[tuple[int, int]], result: int, operator: str):
            self.squares: list[tuple[int, int]] = squares;
            self.result: int = result;
            self.operator: str = operator;
            self.upperLeft: int = 0;
            self.drawPoints: list[tuple[int, int]] = [];
            self.upperLeft = 0;

            self.squares.sort();

    def __init__(self, size: int, seed: int):
        self.size: int = size;
        self.grid: list[list[int]] = [];
        self.lock: list[list[bool]] = [];
        self.cages: list[KenKen.Cage] = [];
        self.verified: bool = False;

        random.seed(seed);

        # Fill out the colors list if its empty
        if len(self.Colors) == 0:
            rgb: int = 255;

            # Past 255/16 (15), colors get too pale/grayish
            while rgb > 15 - 1:
                self.Colors.append((rgb, 0, 0));
                self.Colors.append((0, rgb, 0));
                self.Colors.append((0, 0, rgb));
                self.Colors.append((rgb, rgb, 0));
                self.Colors.append((rgb, 0, rgb));
                self.Colors.append((0, rgb, rgb));
                self.Colors.append((rgb // 2, rgb, 0));
                self.Colors.append((rgb, 0, rgb // 2));
                self.Colors.append((0, rgb // 2, rgb));
                self.Colors.append((rgb, rgb // 2, 0));
                self.Colors.append((rgb // 2, 0, rgb));
                self.Colors.append((0, rgb, rgb // 2));

                rgb = int(rgb / 2);

        if self.size < 3:
            raise ArithmeticError("Ken Ken cannot be smaller than 3");

        for i in range(self.size):
            self.grid.append([]);
            self.lock.append([]);

            for j in range(self.size):
                self.grid[i].append(0);
                self.lock[i].append(False);

    def generate_numbers(self) -> None:
        for i in range(self.size):
            for j in range(self.size):
                self.grid[i][j] = ((i + j) % self.size) + 1;

    def shuffle_numbers(self, display_progress: bool=True) -> None:
        min_shuffles: int = self.size ** 2;
        shuffle_counter: int = 0;

        done: bool = False;
        row_ind: int = 0;
        col_ind: int = 0;
        verified_rows: list[bool] = [False, ] * self.size;
        verified_cols: list[bool] = [False, ] * self.size;

        if display_progress:
            print("Starting shuffle process");

        start_time: float = time.time();

        while not done:
            self.mark_dirty();

            for i in range(self.size):
                # Gather unlocked numbers, randomly distribute into unlocked positions
                unlocked_nums: list[int] = [];

                for j in range(self.size):
                    if not self.lock[i][j]:
                        unlocked_nums.append(self.grid[i][j]);

                random.shuffle(unlocked_nums);

                for j in range(self.size):
                    if not self.lock[i][j]:
                        self.grid[i][j] = unlocked_nums[0];
                        unlocked_nums.pop(0)

            # Once the minimum number of shuffles have been done, start checking verification
            if shuffle_counter > min_shuffles:
                verified_rows[row_ind] = self.verify_row(row_ind);
                verified_cols[col_ind] = self.verify_col(col_ind);

                # If a row and col both verify, lock that number to prevent shuffling it
                if verified_rows[row_ind] and verified_cols[col_ind]:
                    self.lock[row_ind][col_ind] = True;

                col_ind = (col_ind + 1) % self.size;

                if col_ind == 0:
                    row_ind = (row_ind + 1) % self.size;

                if self.verify_all():
                    sec_taken: float = time.time() - start_time;
                    min_taken: float = 0.0;

                    if sec_taken >= 60:
                        min_taken = int(sec_taken / 60.0);
                        sec_taken = sec_taken - (min_taken * 60);

                    if display_progress:
                        print(f"Grid found in: {shuffle_counter - min_shuffles} tries. Took {f'{min_taken} minutes, ' if min_taken  else ''}{sec_taken} seconds.");

                    done = True;

            shuffle_counter += 1;

            if (shuffle_counter % (min_shuffles * 5000)) == 0:
                if display_progress:
                    print(f"{random.choice(self.ProgressMessages)} ...");

                # Periodically unlock everything to prevent getting locked into an impossible solution
                for i in range(self.size):
                    for j in range(self.size):
                        self.lock[i][j] = False;

    def generate_cages(self):
        assigned: list[bool] = [False, ] * (self.size ** 2);

        while False in assigned:
            row: int = random.randint(0, self.size - 1);
            col: int = random.randint(0, self.size - 1);

            if not assigned[row * self.size + col]:
                square_list: list[tuple[int, int]] = [(row, col),];
                assigned[row * self.size + col] = True;

                new_row: int = row;
                new_col: int = col;

                for chance in [85, 30, 10]:
                    if random.randint(0, 100) < chance:
                        tries: int = 10;

                        while tries > 0:
                            direction: int = random.randint(0, 3);

                            if direction == 0 and new_col > 0:
                                if not assigned[new_row * self.size + ((new_col - 1) % self.size)]:
                                    new_col = (new_col - 1) % self.size;

                                    break;
                            elif direction == 1 and new_row < self.size - 1:
                                if not assigned[((new_row + 1) % self.size) * self.size + new_col]:
                                    new_row = (new_row + 1) % self.size;

                                    break;
                            elif direction == 2 and new_col < self.size - 1:
                                if not assigned[new_row * self.size + ((new_col + 1) % self.size)]:
                                    new_col = (new_col + 1) % self.size;

                                    break;
                            elif direction == 3 and new_row > 0:
                                if not assigned[((new_row - 1) % self.size) * self.size + new_col]:
                                    new_row = (new_row - 1) % self.size;

                                    break;

                            tries -= 1;
                        else:
                            break;

                        square_list.append((new_row, new_col));
                        assigned[new_row * self.size + new_col] = True;

                # Pick random operator
                cur_operator: str = "";

                if len(square_list) == 2:
                    cur_operator = random.choice(self.TwoValOperators);
                else:
                    cur_operator = random.choice(self.ThreeValOperators);

                while True:
                    # Calculate result
                    result: int = 0;

                    if cur_operator == '+':
                        for coord in square_list:
                            result += self.grid[coord[0]][coord[1]];

                        break;
                    elif cur_operator == '-':
                        result = self.grid[square_list[0][0]][square_list[0][1]];
                        result -= self.grid[square_list[1][0]][square_list[1][1]];
                        result = abs(result);

                        break;
                    elif cur_operator == '*':
                        result = 1;

                        for coord in square_list:
                            result *= self.grid[coord[0]][coord[1]];

                        break;
                    elif cur_operator == '/':
                        result = self.grid[square_list[0][0]][square_list[0][1]];
                        result /= self.grid[square_list[1][0]][square_list[1][1]];

                        if not result.is_integer():
                            cur_operator = random.choice(self.TwoValOperators);

                            continue;

                        break;
                    else:
                        result = self.grid[square_list[0][0]][square_list[0][1]];

                        break;

                # Make new cage, add to kenken
                self.cages.append(KenKen.Cage(square_list, int(result), cur_operator));

    def generate(self, display_progress: bool=True) -> None:
        self.generate_numbers();
        self.shuffle_numbers(display_progress);
        self.generate_cages();

    def verify_row(self, row_ind: int) -> bool:
        verified: bool = True;
        unique_nums: list[int] = [];

        for num in self.grid[row_ind]:
            if num not in unique_nums:
                unique_nums.append(num);
            else:
                verified = False;
                break;

        return verified;

    def verify_col(self, col_ind: int) -> bool:
        verified: bool = True;
        unique_nums: list[int] = [];
        col: list[int] = [];

        for r in range(self.size):
            col.append(self.grid[r][col_ind]);

        for num in col:
            if num not in unique_nums:
                unique_nums.append(num);
            else:
                verified = False;
                break;

        return verified;

    def verify_all(self) -> bool:
        if not self.verified:
            self.verified = True;

            for i in range(self.size):
                if not self.verify_row(i) or not self.verify_col(i):
                    self.verified = False;
                    break;

        return self.verified;

    def mark_dirty(self) -> None:
        self.verified = False;

        for cage in self.cages:
            cage.drawPoints = [];

    @override
    def __str__(self) -> str:
        result: str = "";

        for row in self.grid:
            for num in row:
                result += f"{num} ";

            result += "\n";

        return result;

    def draw(self, screen: pygame.Surface, draw_x: int, draw_y: int, big_font: pygame.font.Font, small_font: pygame.font.Font, answers: bool = False) -> None:
        cell_width: int = int((screen.get_height() / self.size));
        my_draw_x: int = draw_x;
        my_draw_y: int = draw_y;

        if answers:
            cell_width = int((screen.get_height() / self.size) * .95);
            my_draw_x = draw_x + int((screen.get_height() / self.size) * .05);
            my_draw_y = draw_y + int((screen.get_height() / self.size) * .05);

        half_cell_width: float = cell_width / 2;
        font_height: int = big_font.get_height();
        half_font_height: float = font_height / 2;
        font_char_width: int = big_font.size("0")[0];
        half_font_char_width: float = font_char_width / 2;

        # Draw the main rect
        pygame.draw.rect(screen, (0, 0, 0), (my_draw_x, my_draw_y, cell_width * self.size, cell_width * self.size), 2);

        # Draw the cells
        for i in range(1, self.size):
            pygame.draw.line(screen, (0, 0, 0), (my_draw_x, i * cell_width + my_draw_y), (my_draw_x + (self.size * cell_width), i * cell_width + my_draw_y));
            pygame.draw.line(screen, (0, 0, 0), (i * cell_width + my_draw_x, my_draw_y), (i * cell_width + my_draw_x, (my_draw_y + (self.size * cell_width))));

        # Draw the cages
        for cage in self.cages:
            # Draw the bold lines if a cage has more than 1 square
            if len(cage.squares) > 1:
                # Calculate draw points if empty
                if len(cage.drawPoints) == 0:
                    points: list[tuple[int, int]] = [];
                    buffer: int or float = 0.1;

                    if answers:
                        buffer = int(cell_width * .05);
                    else:
                        buffer = .1;

                    for square in cage.squares:
                        points.append((my_draw_x + ((square[0] + 0) * cell_width) + buffer, my_draw_y + ((square[1] + 0) * cell_width) + buffer));

                    for square in cage.squares:
                        points.append((my_draw_x + ((square[0] + 1) * cell_width) - buffer, my_draw_y + ((square[1] + 0) * cell_width) + buffer));

                    for square in cage.squares:
                        points.append((my_draw_x + ((square[0] + 1) * cell_width) - buffer, my_draw_y + ((square[1] + 1) * cell_width) - buffer));

                    for square in cage.squares:
                        points.append((my_draw_x + ((square[0] + 0) * cell_width) + buffer, my_draw_y + ((square[1] + 1) * cell_width) - buffer));

                    point_dict_x = {};
                    point_dict_y = {};

                    for point in points:
                        x, y = point;

                        if x in point_dict_x:
                            if point not in point_dict_x[x]:
                                point_dict_x[x].append(point);
                        else:
                            point_dict_x[x] = [point, ];

                        if y in point_dict_y:
                            if point not in point_dict_y[y]:
                                point_dict_y[y].append(point);
                        else:
                            point_dict_y[y] = [point, ];

                    for key in point_dict_x:
                        point_dict_x[key].sort();

                    for key in point_dict_y:
                        point_dict_y[key].sort();

                    # For all x/y vals, add the middle points to to_remove
                    # If a point is already in to_remove, remove the point from to_remove
                    to_remove = [];

                    for val in point_dict_x.values():
                        for point in val[1:-1]:
                            if point not in to_remove:
                                to_remove.append(point);
                            else:
                                to_remove.remove(point);

                    for val in point_dict_y.values():
                        for point in val[1:-1]:
                            if point not in to_remove:
                                to_remove.append(point);
                            else:
                                to_remove.remove(point);

                    for point in to_remove:
                        points.remove(point);

                    # Sort the list to draw in the correct order
                    cur_point = 0;
                    cage.drawPoints.append(points.pop(0));

                    while len(points) > 0:
                        if points[cur_point][0] == cage.drawPoints[-1][0] or points[cur_point][1] == cage.drawPoints[-1][1]:
                            cage.drawPoints.append(points.pop(cur_point));
                            cur_point = 0;
                        else:
                            cur_point += 1;

                            if cur_point == len(points):
                                break;

                # If drawing answers, color the cages
                if answers:
                    pygame.draw.lines(screen, self.Colors[self.cages.index(cage)], True, cage.drawPoints, 3);
                else:
                    pygame.draw.lines(screen, (0, 0, 0), True, cage.drawPoints, 3);

            display_info = str(cage.result);

            if len(cage.squares) > 1:
                display_info += cage.operator;

            screen.blit(small_font.render(display_info, True, (0, 0, 0)), (my_draw_x + (cell_width * cage.squares[cage.upperLeft][0]) + (half_cell_width / 2) - half_font_char_width, my_draw_y + (cell_width * cage.squares[cage.upperLeft][1]) + (half_cell_width / 2) - half_font_height));

        # Draw the numbers
        if answers:
            for r in range(len(self.grid)):
                for c in range(len(self.grid[r])):
                    screen.blit(big_font.render(str(self.grid[r][c]), True, (0, 0, 0)), (my_draw_x + (cell_width * (r + 0)) + half_cell_width - half_font_char_width, my_draw_y + (cell_width * (c + 0)) + half_cell_width - half_font_height));

if __name__ == '__main__':
    # Module test
    ken = KenKen(5, random.randrange(sys.maxsize));
    ken.generate(display_progress=False);
    print(ken);