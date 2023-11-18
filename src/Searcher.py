import chess
import chess.polyglot
from TranspositionTable import TT
from MoveOrdering import MoveOrdering
from Evaluation import Evaluation
import time
import os
import random



from Helpers import *
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class SearchDiagnostics:
    def __init__(self):
        self.numCompletedIterations = 0
        self.numPositionsEvaluated = 0
        self.numCutOffs = 0

        self.moveVal = 0
        self.move = chess.Move.null()
        self.eval = 0
        self.moveIsFromPartialSearch = False
        self.NumQChecks = 0
        self.numQMates = 0
        self.isBook = False

        self.maxExtentionReachedInSearch = 0
        
class Searcher:
    def __init__(self, board: chess.Board):
        self.board = board
        self.transpositionTableSizeMB = 64
        self.maxExtentions = 16
        self.immediateMateScore = 1000000
        self.positiveInfinity = 9999999
        self.negativeInfinity = -self.positiveInfinity
        self.CurrentDepth = 0
        self.isPlayingWhite = False
        self.bestMoveThisIteration = chess.Move.null()
        self.bestEvalThisIteration = 0
        self.bestMove = chess.Move.null()
        self.bestEval = 0
        self.hasSearchedAtLeastOneMove = False
        self.searchCancelled = False
        self.searchDiagnostics = SearchDiagnostics()
        self.currentIterationDepth = 0
        self.transpositionTable = TT(board, self.transpositionTableSizeMB)
        self.moveOrderer = MoveOrdering(self.transpositionTable)
        self.evaluation = Evaluation()
        self.debugInfo = ""
        self.searchIterationTimer = 0
        self.searchTotalTimer = 0
        self.Search(1, 0, self.negativeInfinity, self.positiveInfinity)

    
    def UCIInfo(self, depth, score, nodes, time_ms):
        info_str = f"info depth {depth} score {int(score)} nodes {nodes} time {time_ms} nps {nodes*1000//(time_ms if time_ms != 0 else 1000)} pv {self.bestMove.uci()}"
        print(info_str)
    
    def StartSearch(self, event):
        self.bestEvalThisIteration = self.bestEval = 0
        self.bestMoveThisIteration = self.bestMove = chess.Move.null()

        self.isPlayingWhite = self.board.turn == chess.WHITE

        self.moveOrderer.ClearHistory()

        
        # Debug
        self.CurrentDepth = 0
        self.searchCancelled = False
        self.searchDiagnostics = SearchDiagnostics()
        
        self.RunIterativeDeepeningSearch()
        
        if self.bestMove == chess.Move.null():
            self.bestMove = random.choice(list(self.board.legal_moves))
        
        self.searchCancelled = False
        event.set()
        
    def NumPlyToMateFromScore(self, eval):
        return self.immediateMateScore - abs(eval)
        
    def RunIterativeDeepeningSearch(self):
        for searchDepth in range(1, 257):
            self.hasSearchedAtLeastOneMove = False
            self.debugInfo += "\nStarting Iteration: " + str(searchDepth)
            self.searchIterationTimer = time.time()
            self.currentIterationDepth = searchDepth
            #print("<<<< Searching on Depth", searchDepth, "Starting >>>>")
            self.Search(searchDepth, 0, self.negativeInfinity, self.positiveInfinity)
            
            if self.searchCancelled:
                if self.hasSearchedAtLeastOneMove:
                    self.bestMove = self.bestMoveThisIteration
                    self.bestEval = self.bestEvalThisIteration
                    self.searchDiagnostics.move = self.bestMove
                    self.searchDiagnostics.eval = self.bestEval
                    self.searchDiagnostics.moveIsFromPartialSearch = True
                    self.debugInfo += "\nUsing partial search result: " + self.bestMove.uci() + " Eval: " + str(self.bestEval)
                
                self.debugInfo += "\nSearch aborted"
                break
            else:
                self.CurrentDepth = searchDepth     
                self.bestMove = self.bestMoveThisIteration
                self.bestEval = self.bestEvalThisIteration
                self.debugInfo += "\nUsing partial search result: " + self.bestMove.uci() + " Eval: " + str(self.bestEval)

                if IsMateScore(self.bestEval):
                    self.debugInfo += " Mate in ply: " + str(self.NumPlyToMateFromScore(self.bestEval))
                
                self.bestEvalThisIteration = -INF
                self.bestMoveThisIteration = chess.Move.null()
                self.searchDiagnostics.numCompletedIterations = searchDepth
                self.searchDiagnostics.move = self.bestMove
                self.searchDiagnostics.eval = self.bestEval
                
                elapsed_time_ms = int((time.time() - self.searchIterationTimer) * 1000)
                self.UCIInfo(searchDepth, self.bestEval, self.searchDiagnostics.numPositionsEvaluated, elapsed_time_ms)
                
                if IsMateScore(self.bestEval) and self.NumPlyToMateFromScore(self.bestEval) <= searchDepth:
                    self.debugInfo += "\nExitting search due to mate found within search depth"
                    #self.searchCancelled = True
                    break
            

                
    def GetSearchResult(self):
        return (self.bestMove, self.bestEval)
    
    def EndSearch(self):
        self.searchCancelled = True
        
    def Search(self, plyRemaining, plyFromRoot, alpha, beta, numExtensions = 0, prevMove: chess.Move = chess.Move.null(), prevWasCapture = False):
        
        self.searchDiagnostics.numPositionsEvaluated += 1
        if self.searchCancelled:
            return 0
        
        if plyFromRoot > 0:
            if self.board.is_repetition():
                return 0

            alpha = max(alpha, -self.immediateMateScore + plyFromRoot)
            beta = min(beta, self.immediateMateScore - plyFromRoot)
            if alpha >= beta:
                return alpha

        ttVal = self.transpositionTable.LookupEvaluation(plyRemaining, plyFromRoot, alpha, beta)
        if ttVal != LookupFailed:
            if plyFromRoot == 0:
                self.bestMoveThisIteration = self.transpositionTable.TryGetStoredMove()
                self.bestEvalThisIteration = self.transpositionTable.entries[self.transpositionTable.Index()].value
            return ttVal
        
        if plyRemaining == 0:
            return self.QuiescenceSearch(alpha, beta)
        
        moves = list(self.board.legal_moves)
        prevBestMove = self.bestMove if plyFromRoot == 0 else self.transpositionTable.TryGetStoredMove()
        self.moveOrderer.OrderMoves(prevBestMove, self.board, moves, False, plyFromRoot)
        if self.board.is_checkmate():
            mateScore = self.immediateMateScore - plyFromRoot
            return -mateScore
        
        if self.board.is_stalemate():
            return 0
        
        if plyFromRoot > 0:
            wasPawnMove = self.board.piece_type_at(prevMove.from_square) == chess.PAWN
        
        evaluationBound = UpperBound
        self.bestMoveInThisPosition = chess.Move.null()
        
        for i, move in enumerate(moves):
            capturedPieceType = self.board.piece_type_at(move.to_square) if self.board.is_capture(move) else None
            isCapture = capturedPieceType != None
            self.board.push(move)
            extension = 0
            if numExtensions < self.maxExtentions:
                movedPieceType = self.board.piece_type_at(move.to_square)
                targetRank = chess.square_rank(move.to_square)
                if self.board.is_check():
                    extension = 1
                elif (movedPieceType == chess.PAWN and (targetRank == 1 or targetRank == 6)):
                    extension = 1
                    
            needsFullSearch = True
            eval = 0
            
            if(extension == 0 and plyRemaining >= 3 and i >= 3 and not isCapture):
                reduceDepth = 1
                eval = -self.Search(plyRemaining - 1 -reduceDepth, plyFromRoot + 1, -alpha - 1, -alpha, numExtensions, move, isCapture)
                needsFullSearch = eval > alpha
                
            if (needsFullSearch):
                eval = -self.Search(plyRemaining - 1 + extension, plyFromRoot + 1, -beta, -alpha, numExtensions + extension, move, isCapture)

            self.board.pop()
            
            if (self.searchCancelled):
                return 0
            
            if eval >= beta:
                self.transpositionTable.StoreEvaluation(plyRemaining, plyFromRoot, beta, LowerBound, move)
                if not isCapture:
                    if plyFromRoot < self.moveOrderer.maxKillerMovePly:
                        self.moveOrderer.killerMoves[plyFromRoot].Add(move)
                    historyScore = plyRemaining * plyRemaining
                    self.moveOrderer.History[self.board.turn][move.from_square][move.to_square] += historyScore
                
                self.searchDiagnostics.numCutOffs += 1
                return beta
            
            if eval > alpha:
                evaluationBound = Exact
                self.bestMoveInThisPosition = move
                alpha = eval
                
                if plyFromRoot == 0:
                    self.bestMoveThisIteration = move
                    self.bestEvalThisIteration = eval
                    self.hasSearchedAtLeastOneMove = True
        
        
        self.transpositionTable.StoreEvaluation(plyRemaining, plyFromRoot, alpha, evaluationBound, self.bestMoveInThisPosition)
        return alpha
    
    def QuiescenceSearch(self, alpha, beta):
        if self.searchCancelled:
            return 0

        eval = self.evaluation.Evaluate(self.board)
        self.searchDiagnostics.numPositionsEvaluated += 1
        if eval >= beta:
            self.searchDiagnostics.numCutOffs += 1
            return beta
        if eval > alpha:
            alpha = eval
        
        moves = []       
        for mv in list(self.board.legal_moves):
            if self.board.is_capture(mv) or mv.promotion not in [None, chess.KNIGHT]:
                moves.append(mv)
        
        self.moveOrderer.OrderMoves(chess.Move.null(), self.board, moves, True, 0)
        for i, move in enumerate(moves):
            self.board.push(move)
           
            eval = -self.QuiescenceSearch(-beta, -alpha)
            self.board.pop()
            
            if eval >= beta:
                self.searchDiagnostics.numCutOffs += 1
                return beta
            
            if eval > alpha:
                alpha = eval
        return alpha

    def AnnounceMate(self):
        if IsMateScore(self.bestEvalThisIteration):
            numPlyToMate = self.NumPlyToMateFromScore(self.bestEvalThisIteration)
            numMovesToMate = (numPlyToMate + 1) // 2
            sideWithMate = "Black" if (self.bestEvalThisIteration * (1 if self.board.turn == chess.WHITE else -1)) < 0 else "White"
            p = ("s" if numMovesToMate > 1 else "")
            return f"{sideWithMate} can mate in {numMovesToMate} move{p}"
        return "No mate found"
    
    def ClearForNewPosition(self):
        self.transpositionTable.Clear()
        self.moveOrderer.ClearKillers()
    
    def GetTranspositionTable(self):
        return self.transpositionTable


