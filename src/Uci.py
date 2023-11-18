import chess
from Bot import Bot
from Evaluation import Evaluation
class UCI:
    def __init__(self, board: chess.Board):
        self.positionLabels = ["position", "fen", "moves"]
        self.goLabels = ["go", "movetime", "wtime", "btime", "winc", "binc", "movestogo"]
        self.bot = Bot(board)
        self.board = board
        self.evaluation = Evaluation()
        
    def ReceiveCommand(self, message):
        messageType = message.split(" ")[0].lower()
        if messageType == "uci":
            print("id name OBSIDIAN")
            print("id author Imran AKKI")
            print("uciok")
        elif messageType == "isready":
            print("readyok")
        elif messageType == "ucinewgame":
            self.bot.NotifyNewGame()
        elif messageType == "position":
            self.ProcessPositionCommand(message)
        elif messageType == "go":
            self.ProcessGoCommand(message)
        elif messageType == "stop":
            self.bot.StopThinking()
        elif messageType == "quit":
            exit()
        elif messageType == "eval":
            print(self.evaluation.Evaluate(self.board))
        elif messageType == "d":
            print(self.bot.board)
            
    def tryGetLabelledValue(self, text, label, all_labels, default_value=""):
        text = text.strip()
        if label in text:
            value_start = text.index(label) + len(label)
            value_end = len(text)
            for other_id in all_labels:
                if other_id != label and other_id in text:
                    other_id_start_index = text.index(other_id)
                    if value_start < other_id_start_index < value_end:
                        value_end = other_id_start_index

            return text[value_start:value_end].strip()
        
        return default_value

    def ProcessPositionCommand(self, message:str):
        moves_idx = message.find('moves')
        uci_parameters = message.split(' ')
        # get moves from UCI command
        if moves_idx >= 0:
            moveslist = message[moves_idx:].split()[1:]
        else:
            moveslist = []
        
        # get FEN from uci command
        if uci_parameters[1] == 'fen':
            if moves_idx >= 0:
                fenpart = message[:moves_idx]
            else:
                fenpart = message

            _, _, fen = fenpart.split(' ', 2)
        elif uci_parameters[1] == 'startpos':
            fen = chess.STARTING_FEN
        else:
            raise SyntaxError("UCI Syntax error.")

        # start board and make moves
        self.board.set_fen(fen)
        for move in moveslist:
            self.board.push_uci(move)
        
        self.bot.board = self.board
        
                
    def ProcessGoCommand(self, message):
        timeMs = 0
        if "movetime" in message:
            timeMs = int(self.tryGetLabelledValue(message, "movetime", self.goLabels, 0))
        elif "wtime" in message:
            timeRemainingWhiteMs = int(self.tryGetLabelledValue(message, "wtime", self.goLabels, 0))
            timeRemainingBlackMs = int(self.tryGetLabelledValue(message, "btime", self.goLabels, 0))
            incrementWhiteMs = int(self.tryGetLabelledValue(message, "winc", self.goLabels, 0))
            incrementBlackMs = int(self.tryGetLabelledValue(message, "binc", self.goLabels, 0))
            timeMs = self.bot.ChooseThinkTime(timeRemainingWhiteMs, timeRemainingBlackMs, incrementWhiteMs, incrementBlackMs)
        
        else:
            timeMs = 60000
        self.bot.ThinkTimed(timeMs)
    
    
            