import chess
from TranspositionTable import TT
from PSQT import *
from Helpers import *

def GetPieceValue(pieceType: chess.PieceType):
    return pieceValues[pieceType]

class Killer:
    def __init__(self):
        self.moveA = chess.Move.null()
        self.moveB = chess.Move.null()
        
    def Add(self, move: chess.Move):
        if move != self.moveA:
            self.moveB = self.moveA
            self.moveA = move
            
    def Match(self, move: chess.Move):
        return move == self.moveA or move == self.moveB
    

class MoveOrdering:
    def __init__(self, tt: TT):
        
        self.maxMoveCount = 218
        self.squareControlledByOpponentPawnPenalty = 350
        self.capturedPieceValueMultiplier = 100
        self.maxKillerMovePly = 32
        self.million = 1000000
        self.hashMoveScore = self.million * 100
        self.winningCaptureBias = 8 * self.million
        self.promoteBias = 6 * self.million
        self.killerBias = 4 * self.million
        self.losingCaptureBias = 2 * self.million
        self.regularBias = 0
        
        
        self.moveScores = [0] * self.maxMoveCount
        self.tt = tt
        self.invalidMove = chess.Move.null()
        self.killerMoves = [Killer() for i in range(self.maxKillerMovePly)]
        self.History = [[[0] * 64 for i in range(64)] for _ in range(2)]
        
    def ClearHistory(self):
        self.History = [[[0] * 64 for i in range(64)] for _ in range(2)]
        
    def ClearKillers(self):
        self.killerMoves = [Killer() for i in range(self.maxKillerMovePly)]
        
    def Clear(self):
        self.ClearHistory()
        self.ClearKillers()
        
    def OrderMoves(self, hashMove: chess.Move, board: chess.Board, moves, inQSearch, ply):
        pawnAttacks = []
        oppPawnAttacks = []
        oppAttacks = []
        for sq in board.pieces(chess.PAWN, board.turn):
            legal_moves_pawns = filter(lambda move: move.from_square == sq, moves)
            pawnAttacks.extend(legal_moves_pawns)
        for sq in board.pieces(chess.PAWN, not board.turn):
            legal_moves_pawns = filter(lambda move: move.from_square == sq, moves)
            oppPawnAttacks.extend([move.to_square for move in legal_moves_pawns])
        
        for sq in (
            board.pieces(chess.ROOK, not board.turn) |
            board.pieces(chess.KNIGHT, not board.turn) |
            board.pieces(chess.BISHOP, not board.turn) |
            board.pieces(chess.QUEEN, not board.turn) |
            board.pieces(chess.KING, not board.turn)
        ):
            legal_moves = filter(lambda move: move.from_square == sq, moves)
            oppAttacks.extend([move.to_square for move in legal_moves])
        for i, move in enumerate(moves):
            if move == hashMove:
                self.moveScores[i] = self.hashMoveScore
                continue
            
            score = 0
            fromSq = move.from_square
            toSq = move.to_square
            movePiece = board.piece_at(fromSq)
            movePieceType = movePiece.piece_type
            try:
                 capturedPiece = board.piece_at(toSq).piece_type
            except:
                capturedPiece = None
            isCapture = capturedPiece != None
            pieceValue = GetPieceValue(movePieceType)
            
            if isCapture:
                captureMaterialDelta  = GetPieceValue(capturedPiece) - pieceValue
                opponentCanRecapture = board.attackers(not board.turn, toSq) != 0
                if opponentCanRecapture:
                    score += captureMaterialDelta + (self.winningCaptureBias if captureMaterialDelta >= 0 else self.losingCaptureBias)
                else:
                    score += self.winningCaptureBias + captureMaterialDelta
                    
                
            if movePieceType == chess.PAWN:
                if move.promotion != None and not isCapture:
                    score += self.promoteBias
            elif movePieceType == chess.KING:
                pass
            else:
                toScore = TablePSQT[movePieceType][movePiece.color][toSq]
                fromScore = TablePSQT[movePieceType][movePiece.color][fromSq]
                score += toScore - fromScore
                
                if toSq in oppPawnAttacks:
                    score -= 50
                elif toSq in oppAttacks:
                    score -= 25
        
            if not isCapture:
                isKiller = not inQSearch and ply < self.maxKillerMovePly and self.killerMoves[ply].Match(move)
                score += self.killerBias if isKiller else self.regularBias
                score += self.History[board.turn][move.from_square][move.to_square]
                
            self.moveScores[i] = score
        Quicksort(moves, self.moveScores, 0, len(moves) - 1)
        
    def GetScore(self, index):
        score = self.moveScores[index]  
        scoreTypes = [self.hashMoveScore, self.winningCaptureBias, self.losingCaptureBias, self.promoteBias, self.killerMoves, self.regularBias]
        typeNames = ["Hash Move", "Winning Capture", "Losing Capture", "Promotion", "Killer", "Regular"]
        typeName = ""
        closest = INF
        for i in range(len(scoreTypes)):
            delta = abs(score - scoreTypes[i])
            if delta < closest:
                closest = delta
                typeName = typeNames[i]
        
        return f"{score} ({typeName})"
    