import chess
import math
import os
import chess.polyglot
from Searcher import Searcher
import threading
import time
import pkg_resources
import MoveOrdering


class Bot:
    def __init__(self, board: chess.Board):
        self.board = board
        self.searcher = Searcher(board)
        self.useMaxThinkTime = False
        self.maxThinkTimeMs = 2500
        self.isThinking = False
        
    def ChooseThinkTime(self, timeRemainingWhiteMs, timeRemainingBlackMs, incrementWhiteMs, incrementBlackMs):
        board = self.board
        myTimeRemainingMs = timeRemainingWhiteMs if board.turn == chess.WHITE else timeRemainingBlackMs
        myIncrementMs = incrementWhiteMs if board.turn == chess.WHITE else incrementBlackMs
        return math.ceil(min(myTimeRemainingMs / 40 + myIncrementMs, myTimeRemainingMs / 2 - 1))
        
    
    def ThinkTimed(self, timeMs):
        self.isThinking = True
        try:
            binary_data = pkg_resources.resource_filename(__name__, "Titans.bin")
            move = chess.polyglot.MemoryMappedReader(binary_data).weighted_choice(self.board).move
            self.searcher.bestMove = move
                
            print("bestmove", move.uci())
        except:
            self.StartSearch(timeMs)
            
    def StopThinking(self):
        if self.isThinking:
            self.searcher.EndSearch()
            self.isThinking = False
    
    def StartSearch(self, timeMs):
        self.searcher.board = self.board
        event = threading.Event()
        copy = self.board.copy()
        thread1 = threading.Thread(target=self.searcher.StartSearch, args=(event,))
        thread2 = threading.Thread(target=self.StopThinking)
        thread1.start()
        event.wait(timeMs // 1000)
        thread2.start()
        move, eval = self.searcher.GetSearchResult()
        if move == chess.Move.null():
            movesList = list(copy.legal_moves)
            self.searcher.moveOrderer.OrderMoves(chess.Move.null(), copy, movesList, False, 0)
            move = movesList[0]
        print("bestmove", move.uci())
        
    def NotifyNewGame(self):
        self.board.reset()
        self.searcher.ClearForNewPosition()