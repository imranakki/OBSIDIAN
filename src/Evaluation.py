import chess
from PSQT import *

# Performs static evaluation of the current position.
# The position is assumed to be 'quiet', i.e no captures are available that could drastically affect the evaluation.
# The score that's returned is given from the perspective of whoever's turn it is to move.
# So a positive score means the player who's turn it is to move has an advantage, while a negative score indicates a disadvantage.

class MaterialInfo:
    def __init__(self, board: chess.Board, isWhite:bool):
        self.pawns = len(board.pieces(chess.PAWN, isWhite))
        self.knights = len(board.pieces(chess.KNIGHT, isWhite))
        self.bishops = len(board.pieces(chess.BISHOP, isWhite))
        self.rooks = len(board.pieces(chess.ROOK, isWhite))
        self.queens = len(board.pieces(chess.QUEEN, isWhite))
        self.myPawns = board.pieces(chess.PAWN, isWhite)
        self.enemyPawns = board.pieces(chess.PAWN, not isWhite)
        
        self.numMajors = self.queens + self.rooks
        self.numMinors = self.knights + self.bishops
        
        self.materialScore = 0
        self.materialScore += self.pawns * pieceValues[chess.PAWN]
        self.materialScore += self.knights * pieceValues[chess.KNIGHT]
        self.materialScore += self.bishops * pieceValues[chess.BISHOP]
        self.materialScore += self.rooks * pieceValues[chess.ROOK]
        self.materialScore += self.queens * pieceValues[chess.QUEEN]
        
        # Endgame Transition (0->1)
        queenEndgameWeight = 45
        rookEndgameWeight = 20
        bishopEndgameWeight = 10
        knightEndgameWeight = 10
        
        endgameStartWeight = 2 * rookEndgameWeight + 2 * bishopEndgameWeight + 2 * knightEndgameWeight + queenEndgameWeight
        endgameWeightSum = self.queens * queenEndgameWeight + self.rooks * rookEndgameWeight + self.bishops * bishopEndgameWeight + self.knights * knightEndgameWeight
        
        self.endgameScore = 1 - min(1, endgameWeightSum / endgameStartWeight)

class EvalData:
    def __init__(self):
        self.materialScore = 0
        self.mopUpScore = 0
        self.pieceSquareScore = 0
        self.pawnScore = 0
        self.pawnShieldScore = 0

    def Sum(self):
        
        return self.materialScore + self.mopUpScore + self.pieceSquareScore + self.pawnScore + self.pawnShieldScore
         
       
class Evaluation:
    def MaterialScore(self, board, isWhite):
        m = MaterialInfo(board, isWhite)
        return m.materialScore

    def EvaluatePieceSquareTable(self, board, isWhite, endgameScore):
        
        def EvaluatePiece(pieceType, pieceSquareTable):
            score = 0
            for square in board.pieces(pieceType, isWhite):
                score += pieceSquareTable[square]
            return score
        
        score = 0
        
        score += EvaluatePiece(chess.KNIGHT, Knights)
        score += EvaluatePiece(chess.BISHOP, Bishops)
        score += EvaluatePiece(chess.ROOK, Rooks)
        score += EvaluatePiece(chess.QUEEN, Queens)
        
        pawnEarly = EvaluatePiece(chess.PAWN, Pawns)
        pawnEnd = EvaluatePiece(chess.PAWN, PawnsEnd)
        score += pawnEarly * (1 - endgameScore) + pawnEnd * endgameScore
        
        kingEarly = EvaluatePiece(chess.KING, King)
        kingEnd = EvaluatePiece(chess.KING, KingEnd)
        score += kingEarly * (1 - endgameScore) + kingEnd * endgameScore
        return score
        
    def EndgamePhaseWeight(self, materialCountWithoutPawns):
        multiplier = 1 / endgameMaterialStart
        return 1 - min(1, multiplier * materialCountWithoutPawns)

    def distanceToCenterSquares(self, square):
        return min(chess.square_distance(square, chess.E4), chess.square_distance(square, chess.D4), chess.square_distance(square, chess.E5), chess.square_distance(square, chess.D5))
     
    
    # As game transitions to endgame, and if up material, then encourage moving king closer to opponent king    
    def MopUpEval(self, board: chess.Board, isWhite: bool, friendlyMaterial, enemyMaterial):

        if friendlyMaterial.materialScore > enemyMaterial.materialScore + 2 * pieceValues[chess.PAWN] and enemyMaterial.endgameScore > 0:
            score = 0
            friendKing = board.king(isWhite)
            enemyKing = board.king(not isWhite)
            # Encourage moving king closer to opponent king
            score += (14 - chess.square_distance(friendKing, enemyKing)) * 4
            # Encourage pushing opponent king to edge of board
            score += self.distanceToCenterSquares(enemyKing) * 10
            return score * enemyMaterial.endgameScore
        
        return 0

    def EvaluatePawn(self, board: chess.Board, isWhite):
        fpanws = set(chess.square_file(sq) for sq in board.pieces(chess.PAWN, isWhite))
        epawnsFiles = set(chess.square_file(sq) for sq in board.pieces(chess.PAWN, not isWhite))

        # Is passed pawn
        def passedPawn():
            score = 0
            for sq in fpanws:
                if sq not in epawnsFiles:
                    rank = chess.square_rank(sq) if not isWhite else 6 - chess.square_rank(sq)
                    score += passedPawnBonuses[rank]
            return score
        
        # Is isolated pawn
        def isolatedPawn():
            cnt = 0
            for sq in fpanws:
                file = chess.square_file(sq)
                if file - 1 not in fpanws and file + 1 not in fpanws:
                    cnt += 1
                    
            return isolatedPawnPenaltyByCount[cnt]
        
        
        return passedPawn() + isolatedPawn()
                
    def Clamp(self, x, min, max):
        if x < min:
            return min
        if x > max:
            return max
        return x

    def KingPawnSheild(self, board: chess.Board, isWhite: bool, enemyMaterial:MaterialInfo, enemyPieceSquareScore):
        enemyMaterial = MaterialInfo(board, not isWhite)
        if enemyMaterial.endgameScore >= 1:
            return 0
        
        penalty = 0
        friendlyPawns = board.pieces(chess.PAWN, isWhite)
        king = board.king(isWhite)
        kingFile = chess.square_file(king)
        uncastleKingPenalty = 0
        
        shieldWhite = shieldBlack = []
        sq = king
        rank = chess.square_rank(sq)
        file = chess.square_file(sq)
        for fileOffset in range(-1, 2):
            if file + fileOffset >= 0 and file + fileOffset <= 7 and rank + 1 >= 0 and rank + 1 <= 7:
                shieldWhite.append(chess.square(file + fileOffset, rank + 1))
                shieldBlack.append(chess.square(file + fileOffset, rank - 1))

        for fileOffset in range(-1, 2):
            if file + fileOffset >= 0 and file + fileOffset <= 7 and rank + 2 >= 0 and rank + 2 <= 7:
                shieldWhite.append(chess.square(file + fileOffset, rank + 2))
                shieldBlack.append(chess.square(file + fileOffset, rank - 2))
        
        if kingFile <= 2 or kingFile >= 5:
            squares = shieldWhite if isWhite else shieldBlack
            for i in range(len(squares) // 2):
                sq = squares[i]
                if sq not in friendlyPawns:
                    if len(squares) > 3 and i + 3 < len(squares) and squares[i + 3] in friendlyPawns and (i+3 < len(kingPawnShieldScores)):
                        penalty += kingPawnShieldScores[i + 3]
                    else:
                        penalty += kingPawnShieldScores[i]
            penalty *= penalty
        else:
            enemyDevelopementScore = self.Clamp((enemyPieceSquareScore + 10) / 130.0, 0, 1)
            uncastleKingPenalty = 50 * enemyDevelopementScore
            
        openFileAgainstKingPenalty  = 0
        epawnsFiles = set(chess.square_file(sq) for sq in board.pieces(chess.PAWN, not isWhite))
        fpawnsFiles = set(chess.square_file(sq) for sq in board.pieces(chess.PAWN, isWhite))
        if enemyMaterial.rooks > 1 or (enemyMaterial.rooks == 1 and enemyMaterial.queens > 0):
            clampedKingFile = self.Clamp(kingFile, 1, 6)
            for attack in range(clampedKingFile, clampedKingFile+2):
                isKingFile = attack == kingFile
                if attack not in epawnsFiles:
                    openFileAgainstKingPenalty += 25 if isKingFile else 15
                    if attack not in fpawnsFiles:
                        openFileAgainstKingPenalty += 15 if isKingFile else 10
        pawnShieldWeight = 1 - enemyMaterial.endgameScore
        if (len(board.pieces(chess.QUEEN, not isWhite)) == 0):
            pawnShieldWeight *= 0.6
            
        return (int)((-penalty - uncastleKingPenalty - openFileAgainstKingPenalty) * pawnShieldWeight)

    def Evaluate(self, board):
        whiteEval = EvalData()
        blackEval = EvalData()
        whiteMaterial = MaterialInfo(board, True)
        blackMaterial = MaterialInfo(board, False)
        
        # Score based on number (and type) of pieces on board
        whiteEval.materialScore = whiteMaterial.materialScore
        blackEval.materialScore = blackMaterial.materialScore
        
        # Score based on positions of pieces
        whiteEval.pieceSquareScore = self.EvaluatePieceSquareTable(board, True, blackMaterial.endgameScore)
        blackEval.pieceSquareScore = self.EvaluatePieceSquareTable(board, False, whiteMaterial.endgameScore)
        
        # Encourage using own king to push enemy king to edge of board in winning endgame
        whiteEval.mopUpScore = self.MopUpEval(board, True, whiteMaterial, blackMaterial)
        blackEval.mopUpScore = self.MopUpEval(board, False, blackMaterial, whiteMaterial)
        
        whiteEval.pawnScore = self.EvaluatePawn(board, True)
        blackEval.pawnScore = self.EvaluatePawn(board, False)
        
        whiteEval.pawnShieldScore = self.KingPawnSheild(board, True, blackMaterial, blackEval.pieceSquareScore)
        blackEval.pawnShieldScore = self.KingPawnSheild(board, False, whiteMaterial, whiteEval.pieceSquareScore)
        
        pres = 1 if board.turn else -1
        return pres * (whiteEval.Sum() - blackEval.Sum())
