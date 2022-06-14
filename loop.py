#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 10:15:22 2021

@author: winpratt
"""

#Initialize

import copy
import random
from itertools import islice
import requests
from lxml import etree
import pandas as pd
import math
#%% Puzzle

base  = 3
side  = base*base

# pattern for a baseline valid solution
def pattern(r,c): return (base*(r%base)+r//base+c)%side


games = pd.DataFrame(columns = ['game','solution','difficulty'])
runs = 0
gl = 0


leng = 30
lowlim = leng//10


while runs < leng:
    
    runs += 1
    
    # randomize rows, columns and numbers (of valid base pattern)
    from random import sample
    def shuffle(s): return sample(s,len(s)) 
    rBase = range(base) 
    rows  = [ g*base + r for g in shuffle(rBase) for r in shuffle(rBase) ] 
    cols  = [ g*base + c for g in shuffle(rBase) for c in shuffle(rBase) ]
    nums  = shuffle(range(1,base*base+1))
    
    # produce board using randomized baseline pattern
    board = [ [nums[pattern(r,c)] for c in cols] for r in rows ]
    
    brd = [str(item) for sublist in board for item in sublist]
    brdstr = ''.join(brd)
    #print(brdstr)
    
    problem = copy.deepcopy(board)
    
    #for line in board: print(line)
    
    
    # Print Board
    def expandLine(line):
        return line[0]+line[5:9].join([line[1:5]*(base-1)]*base)+line[9:13]
    line0  = expandLine("╔═══╤═══╦═══╗")
    line1  = expandLine("║ . │ . ║ . ║")
    line2  = expandLine("╟───┼───╫───╢")
    line3  = expandLine("╠═══╪═══╬═══╣")
    line4  = expandLine("╚═══╧═══╩═══╝")
    
    symbol = " 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    nums   = [ [""]+[symbol[n] for n in row] for row in board ]
    #print(line0)
    #for r in range(1,side+1):
    #    print( "".join(n+s for n,s in zip(nums[r-1],line1.split("."))) )
    #    print([line2,line3,line4][(r%side==0)+(r%base==0)])
        
    # Remove Numbers
    squares = side*side
    empties = squares * 4//5
    for p in sample(range(squares),empties):
        problem[p//side][p%side] = 0
    
    numSize = len(str(side))
    #for line in problem: print("["+"  ".join(f"{n or '.':{numSize}}" for n in line)+"]")
    
    def expandLine(line):
        return line[0]+line[5:9].join([line[1:5]*(base-1)]*base)+line[9:13]
    line0  = expandLine("╔═══╤═══╦═══╗")
    line1  = expandLine("║ . │ . ║ . ║")
    line2  = expandLine("╟───┼───╫───╢")
    line3  = expandLine("╠═══╪═══╬═══╣")
    line4  = expandLine("╚═══╧═══╩═══╝")
    
    symbol = " 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    nums   = [ [""]+[symbol[n] for n in row] for row in problem ]
    #print(line0)
    #for r in range(1,side+1):
    #    print( "".join(n+s for n,s in zip(nums[r-1],line1.split("."))) )
    #    print([line2,line3,line4][(r%side==0)+(r%base==0)])
    
    
    # Solver Function
    def shortSudokuSolve(board):
        size    = len(board)
        block   = int(size**0.5)
        board   = [n for row in board for n in row ]      
        span    = { (n,p): { (g,n)  for g in (n>0)*[p//size, size+p%size, 2*size+p%size//block+p//size//block*block] }
                    for p in range(size*size) for n in range(size+1) }
        empties = [i for i,n in enumerate(board) if n==0 ]
        used    = set().union(*(span[n,p] for p,n in enumerate(board) if n))
        empty   = 0
        while empty>=0 and empty<len(empties):
            pos        = empties[empty]
            used      -= span[board[pos],pos]
            board[pos] = next((n for n in range(board[pos]+1,size+1) if not span[n,pos]&used),0)
            used      |= span[board[pos],pos]
            empty     += 1 if board[pos] else -1
            if empty == len(empties):
                solution = [board[r:r+size] for r in range(0,size*size,size)]
                yield solution
                empty -= 1
    

    while True:
        solved  = [*islice(shortSudokuSolve(problem),2)]
        if len(solved)==1:break
        diffPos = [(r,c) for r in range(9) for c in range(9)
                   if solved[0][r][c] != solved[1][r][c] ] 
        r,c = random.choice(diffPos)
        problem[r][c] = board[r][c]
    
    symbol = " 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    nums   = [ [""]+[symbol[n] for n in row] for row in problem ]
    #print(line0)
    #for r in range(1,side+1):
    #    print( "".join(n+s for n,s in zip(nums[r-1],line1.split("."))) )
    #    print([line2,line3,line4][(r%side==0)+(r%base==0)])
        
    # Difficulty
    prob = [str(item) for sublist in problem for item in sublist]
    prbstr = ''.join(prob)
    #print(prbstr)
    
    base_url = "https://www.thonky.com/sudoku/evaluate-sudoku?puzzlebox="
    url = base_url + str(prbstr)
    
    response = requests.get(url)
    
    html = etree.HTML(response.text)
    nodess = html.xpath('//*[@id="body-text"]/article/span/div/p[2]/big/text()')
    diffstr = [str(x) for x in nodess][1]
    res = [int(i) for i in diffstr.split() if i.isdigit()][0]
    
    
    
    tempgl = len(games[games['difficulty'] == res])
    
    if res <= 2 and tempgl > lowlim:
        flg = 0
    else:
        flg = 1
    
   
    if flg == 1:
        row = [prbstr, brdstr, res]
        games.loc[gl] = row
        print(str(runs) + ': ' + str(res))
    
    gl = len(games)
    

print(games.groupby(['difficulty']).count())
