#-------------------------------------------------------------------------------
# Name:        KenKen
# Purpose:     Encapsulate all the functions needed to interact with
#               mathematic Ken Ken puzzles
#
# Author:      Dustin L. Gehm
#
# Created:     07/11/2017
# Copyright:   (c) Dustin 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import random;
import pygame;

class KenKen:
    Colors = [];

    class Cage:
        def __init__(self, squares, result, operator):
            self.squares = squares;
            self.result = result;
            self.operator = operator;
            self.upperLeft = 0;
            self.drawPoints = [];

            self.squares.sort();

##            for i in range(1, len(self.squares)):
##                if self.squares[i][0] < self.squares[self.upperLeft][0]:
##                    self.upperLeft = i;
##
##            for i in range(len(self.squares)):
##                if self.squares[i][1] < self.squares[self.upperLeft][1]:
##                    self.upperLeft = i;

            self.upperLeft = 0;

    def __init__(self, integer, seed):
        self.size = integer;
        self.grid = [];
        self.lock = [];
        self.cages = [];
        self.verified = None;

        random.seed(seed);

        #fill out the colors list if its empty
        if len(self.Colors) == 0:
            rgb = 255;

            while rgb > 15 - 1:
                self.Colors.append((rgb, 0, 0));
                self.Colors.append((0, rgb, 0));
                self.Colors.append((0, 0, rgb));
                self.Colors.append((rgb, rgb, 0));
                self.Colors.append((rgb, 0, rgb));
                self.Colors.append((0, rgb, rgb));
                self.Colors.append((rgb / 2, rgb, 0));
                self.Colors.append((rgb, 0, rgb / 2));
                self.Colors.append((0, rgb / 2, rgb));
                self.Colors.append((rgb, rgb / 2, 0));
                self.Colors.append((rgb / 2, 0, rgb));
                self.Colors.append((0, rgb, rgb / 2));

                rgb = int(rgb / 2);

        if(self.size < 3):
            raise ArithmeticError("Ken Ken cannot be smaller than 3");

        for i in range(self.size):
            self.grid.append([]);
            self.lock.append([]);

            for j in range(self.size):
                self.grid[i].append(0);
                self.lock[i].append(False);

    def generateNumbers(self):
        for i in range(self.size):
            for j in range(self.size):
                self.grid[i][j] = ((i + j) % self.size) + 1;

    def shuffleNumbers(self):
        minShuffles = int((self.size ** 2));
        curShuffles = 0;

        done = False;
        rotRowInd = 0;
        rotColInd = 0;
        verifiedRows = [False, ] * self.size;
        verifiedCols = [False, ] * self.size;

        while not done:
            self.markDirty();
            for i in range(self.size):
                unlockedNums = [];
                for j in range(self.size):
                    if not self.lock[i][j]:
                        unlockedNums.append(self.grid[i][j]);

                random.shuffle(unlockedNums);

                for j in range(self.size):
                    if not self.lock[i][j]:
                        self.grid[i][j] = unlockedNums[0];
                        unlockedNums = unlockedNums[1:];

            if curShuffles > minShuffles:
                verifiedRows[rotRowInd] = self.verifyRow(rotRowInd);
                verifiedCols[rotColInd] = self.verifyCol(rotColInd);

                if verifiedRows[rotRowInd] and verifiedCols[rotColInd]:
                    self.lock[rotRowInd][rotColInd] = True;

                rotColInd = (rotColInd + 1) % self.size;
                if rotColInd == 0:
                    rotRowInd = (rotRowInd + 1) % self.size;

                if self.verify():
                    print("Grid found in: ", curShuffles - minShuffles, " tries.");
                    done = True;

            curShuffles += 1;

            if (curShuffles % (minShuffles * 5000)) == 0:
                print("...");
                for i in range(self.size):
                    for j in range(self.size):
                        self.lock[i][j] = False;

    def generateCages(self):
        assigned = [False, ] * (self.size ** 2);

        while False in assigned:
            rowInd = random.randint(0, self.size - 1);
            colInd = random.randint(0, self.size - 1);

            if assigned[rowInd * self.size + colInd] == False:
                squareList = [];
                squareList.append((rowInd, colInd));
                assigned[rowInd * self.size + colInd] = True;

                newRowInd = rowInd;
                newColInd = colInd;

                for chance in [85, 30, 10]:
                    if random.randint(0, 100) < chance:
                        tries = 10;
                        while tries > 0:
                            direction = random.randint(0, 3);

                            if direction == 0 and newColInd > 0:
                                if assigned[newRowInd * self.size + ((newColInd - 1) % self.size)] == False:
                                    newColInd = (newColInd - 1) % self.size;
                                    break;
                            elif direction == 1 and newRowInd < self.size - 1:
                                if assigned[((newRowInd + 1) % self.size) * self.size + newColInd] == False:
                                    newRowInd = (newRowInd + 1) % self.size;
                                    break;
                            elif direction == 2 and newColInd < self.size - 1:
                                if assigned[newRowInd * self.size + ((newColInd + 1) % self.size)] == False:
                                    newColInd = (newColInd + 1) % self.size;
                                    break;
                            elif direction == 3 and newRowInd > 0:
                                if assigned[((newRowInd - 1) % self.size) * self.size + newColInd] == False:
                                    newRowInd = (newRowInd - 1) % self.size;
                                    break;
                            tries -= 1;
                        else:
                            break;

                        squareList.append((newRowInd, newColInd));
                        assigned[newRowInd * self.size + newColInd] = True;

                #pick random operator
                curOperator = "";
                twoValOperators = ['+', '-', '*', '/'];
                threeValOperators = ['+', '*'];

                if len(squareList) == 2:
                    curOperator = twoValOperators[random.randint(0, len(twoValOperators) - 1)];
                else:
                    curOperator = threeValOperators[random.randint(0, len(threeValOperators) - 1)];

                while True:
                    #calculate result
                    curResult = 0;
                    if curOperator == '+':
                        for coord in squareList:
                            curResult += self.grid[coord[0]][coord[1]];
                        break;
                    elif curOperator == '-':
                        curResult = self.grid[squareList[0][0]][squareList[0][1]];
                        curResult -= self.grid[squareList[1][0]][squareList[1][1]];
                        curResult = abs(curResult);
                        break;
                    elif curOperator == '*':
                        curResult = 1;
                        for coord in squareList:
                            curResult *= self.grid[coord[0]][coord[1]];
                        break;
                    elif curOperator == '/':
                        curResult = self.grid[squareList[0][0]][squareList[0][1]];
                        curResult /= self.grid[squareList[1][0]][squareList[1][1]];

                        if not curResult.is_integer():
                            curOperator = twoValOperators[random.randint(0, len(twoValOperators) - 1)];
                            continue;

                        break;
                    else:
                        curResult = self.grid[squareList[0][0]][squareList[0][1]];
                        break;

                #make new cage, add to kenken
                newCage = KenKen.Cage(squareList, int(curResult), curOperator);
                self.cages.append(newCage);

    def generate(self):
        self.generateNumbers();
        self.shuffleNumbers();
        self.generateCages();

    def verifyRow(self, rowInd):
        rowVerified = True;
        uniqueNums = [];

        for num in self.grid[rowInd]:
            if num not in uniqueNums:
                uniqueNums.append(num);
            else:
                rowVerified = False;
                break;

        return rowVerified;

    def verifyCol(self, colInd):
        colVerified = True;
        uniqueNums = [];
        col = [];
        for r in range(self.size):
            col.append(self.grid[r][colInd]);

        for num in col:
            if num not in uniqueNums:
                uniqueNums.append(num);
            else:
                colVerified = False;
                break;

        return colVerified;

    def verify(self):
        if self.verified is None:
            self.verified = True;

            for i in range(self.size):
                if not self.verifyRow(i) or not self.verifyCol(i):
                    self.verified = False;
                    break;

        return self.verified;

    def markDirty(self):
        self.verified = None;

        for cage in self.cages:
            cage.drawPoints = [];

    def prnt(self):
        for row in self.grid:
            for num in row:
                print(num, end = " ");

            print("");

    def draw(self, screen, drawx, drawy, bigFontObj, smallFontObj, answers = False):
        cellWidth = 0;
        mydrawx = 0;
        mydrawy = 0;

        if answers:
            cellWidth = int((screen.get_height() / self.size) * .95);
            mydrawx = drawx + int((screen.get_height() / self.size) * .05);
            mydrawy = drawy + int((screen.get_height() / self.size) * .05);
        else:
            cellWidth = int((screen.get_height() / self.size));
            mydrawx = drawx;
            mydrawy = drawy;

        halfCellWidth = cellWidth / 2;
        fontHeight = bigFontObj.get_height();
        halfFontHeight = fontHeight / 2;
        fontCharWidth = bigFontObj.size("0")[0];
        halfFontCharWidth = fontCharWidth / 2;

        #draw the main rect
        pygame.draw.rect(screen, (0, 0, 0), (mydrawx, mydrawy, cellWidth * self.size, cellWidth * self.size), 2);

        #draw the cells
        for i in range(1, self.size):
            pygame.draw.line(screen, (0, 0, 0), (mydrawx, i * cellWidth + mydrawy), (mydrawx + (self.size * cellWidth), i * cellWidth + mydrawy));
            pygame.draw.line(screen, (0, 0, 0), (i * cellWidth + mydrawx, mydrawy), (i * cellWidth + mydrawx, (mydrawy + (self.size * cellWidth))));

        #draw the cages
        for cage in self.cages:
            #draw the bold lines if a cage has more than 1 square
            if len(cage.squares) > 1:
                #calculate draw points if empty
                if len(cage.drawPoints) == 0:
                    points = [];
                    if answers:
                        buffer = int(cellWidth * .05);
                    else:
                        buffer = .1;

                    for square in cage.squares:
                        points.append((mydrawx + ((square[0] + 0) * cellWidth) + buffer, mydrawy + ((square[1] + 0) * cellWidth) + buffer));
                    for square in cage.squares:
                        points.append((mydrawx + ((square[0] + 1) * cellWidth) - buffer, mydrawy + ((square[1] + 0) * cellWidth) + buffer));
                    for square in cage.squares:
                        points.append((mydrawx + ((square[0] + 1) * cellWidth) - buffer, mydrawy + ((square[1] + 1) * cellWidth) - buffer));
                    for square in cage.squares:
                        points.append((mydrawx + ((square[0] + 0) * cellWidth) + buffer, mydrawy + ((square[1] + 1) * cellWidth) - buffer));

                    pointDictX = {};
                    pointDictY = {};
                    for point in points:
                        x, y = point;

                        if x in pointDictX.keys():
                            if point not in pointDictX[x]:
                                pointDictX[x].append(point);
                        else:
                            pointDictX[x] = [point, ];

                        if y in pointDictY.keys():
                            if point not in pointDictY[y]:
                                pointDictY[y].append(point);
                        else:
                            pointDictY[y] = [point, ];

                    for key in pointDictX.keys():
                        pointDictX[key].sort();

                    for key in pointDictY.keys():
                        pointDictY[key].sort();

                    #for all x/y vals, add the center points to toRemove
                    # if a point is already in toRemove, dont add and remove the point from toRemove
                    toRemove = [];
                    for val in pointDictX.values():
                        for point in val[1:-1]:
                            if point not in toRemove:
                                toRemove.append(point);
                            else:
                                toRemove.remove(point);

                    for val in pointDictY.values():
                        for point in val[1:-1]:
                            if point not in toRemove:
                                toRemove.append(point);
                            else:
                                toRemove.remove(point);

                    for point in toRemove:
                        points.remove(point);

                    #sort the list to draw in the correct order
                    curPoint = 0;
                    cage.drawPoints.append(points.pop(0));

                    while(len(points) > 0):
                        if points[curPoint][0] == cage.drawPoints[-1][0] \
                           or points[curPoint][1] == cage.drawPoints[-1][1]:
                            cage.drawPoints.append(points.pop(curPoint));
                            curPoint = 0;
                        else:
                            curPoint += 1;

                            if curPoint == len(points):
                                break;

                if answers:
                    pygame.draw.lines(screen, self.Colors[self.cages.index(cage)], True, cage.drawPoints, 3);
                else:
                    pygame.draw.lines(screen, (0, 0, 0), True, cage.drawPoints, 3);

            displayInfo = str(cage.result);
            if len(cage.squares) > 1:
                displayInfo += cage.operator;

            screen.blit(smallFontObj.render(displayInfo, False, (0, 0, 0)), (mydrawx + (cellWidth * cage.squares[cage.upperLeft][0]) + (halfCellWidth / 2) - halfFontCharWidth, mydrawy + (cellWidth * cage.squares[cage.upperLeft][1]) + (halfCellWidth / 2) - halfFontHeight));

        #draw the numbers
        if answers:
            for r in range(len(self.grid)):
                for c in range(len(self.grid[r])):
                    screen.blit(bigFontObj.render(str(self.grid[r][c]), False, (0, 0, 0)), (mydrawx + (cellWidth * (r + 0)) + halfCellWidth - halfFontCharWidth, mydrawy + (cellWidth * (c + 0)) + halfCellWidth - halfFontHeight));

if __name__ == '__main__':
    ken = KenKen(5, 66342);
    ken.generate();
    ken.prnt();