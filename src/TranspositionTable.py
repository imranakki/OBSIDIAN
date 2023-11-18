import chess
import sys
import chess.polyglot
from Helpers import *
from constants import *

class Entry:
    def __init__(self, key, value, depth, flag, move: chess.Move):
        self.key = key
        self.value = value
        self.depth = depth
        self.nodeType = flag
        self.move = move
        
    def getSize():
        try:
            return sys.getsizeof(Entry)
        except:
            return 0

class TT:
    
    def __init__(self, board: chess.Board, sizeMB):
        self.board = board
        ttEntrySizeBytes = sys.getsizeof(Entry)
        self.count  = int(sizeMB * 1024 * 1024 / ttEntrySizeBytes)
        self.entries = [Entry(0, 0, 0, 0, chess.Move.null()) for i in range(self.count)]
        self.enabled = True
    
    def Clear(self):
        self.entries = [Entry(0, 0, 0, 0, chess.Move.null()) for i in range(self.count)]
        
    def Index(self):
        return chess.polyglot.zobrist_hash(self.board) % self.count
    
    def TryGetStoredMove(self):
        return self.entries[self.Index()].move
    
    def CorrectRetrievedMateScore(self, score, numPlySearched):
        if IsMateScore(score):
            sign = 1 if score > 0 else -1
            return (score * sign - numPlySearched) * sign

        return score
    
    def CorrectMateScoreForStorage(self, score, numPlySearched):
        if IsMateScore(score):
            sign = 1 if score > 0 else -1
            return (score * sign + numPlySearched) * sign

        return score
    
    def LookupEvaluation(self, depth, plyFromRoot, alpha, beta):
        if not self.enabled:
            return self.LookupFailed
        
        entry: Entry = self.entries[self.Index()]
        if entry.key == chess.polyglot.zobrist_hash(self.board):
            if entry.depth >= depth:
                correctedScore = self.CorrectRetrievedMateScore(entry.value, plyFromRoot)

                if entry.nodeType == Exact:
                    return correctedScore
                
                if entry.nodeType == UpperBound and correctedScore <= alpha:
                    return correctedScore
                
                if entry.nodeType == LowerBound and correctedScore >= beta:
                    return correctedScore
        return LookupFailed
                
    def StoreEvaluation(self, depth, numPlySearched, eval, evalType, move:chess.Move):
        if not self.enabled:
            return
        
        index = self.Index()
        entry = Entry(chess.polyglot.zobrist_hash(self.board), self.CorrectMateScoreForStorage(eval, numPlySearched), depth, evalType, move)
        self.entries[index] = entry
        
    def getEntry(self, zobristKey):
        return self.entries[zobristKey % self.count]
    
        
        
    
