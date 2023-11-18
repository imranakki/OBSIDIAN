import chess
from Uci import UCI

board = chess.Board()
uci = UCI(board)
while True:
    text = input()
    uci.ReceiveCommand(text)