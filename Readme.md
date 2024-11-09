
# OBSIDIAN CHESS ENGINE

  

![OBSIDIAN Logo](https://i.ibb.co/bm0GNRq/OBSIDIANCHESS.png)

  

## Say Hello to OBSIDIAN!

  

Meet OBSIDIAN, your free chess-playing companion written in Python. It may not be the fanciest, but it's like having your very own chess expert in your computer. With OBSIDIAN, you get a reliable chess partner that plays at a strong level, around 2000 ELO. Let's dive into the world of chess together!

  

## How to Get Started

  

1.  **Install Python**: Get it from the [official website](https://www.python.org/downloads/).

2.  **Get OBSIDIAN Ready**: Open your terminal and run `pip install -r requirements.txt`.

3.  **Bring OBSIDIAN In**: Clone the repository or download the ZIP file and unzip it.

  

## Play a Game with OBSIDIAN!

  

Challenge OBSIDIAN to a game using user-friendly interfaces like [PyChess](https://pychess.github.io/download/) or [Arena](http://www.playwitharena.de/).

  

## Features

  

**Search Algorithms:**

1. Minimax Algorithm

2. Alpha-Beta Pruning

3. Quiescence Search

  
  

**Move Ordering:**

1. History Heuristic

2. Killer Moves

3. Static Exchange Evaluation (SEE)

4. Piece-Square Tables (PSQT)

5. Promotion Bias

6. Square Control Penalty

7. Capture and Promotion Scoring

8. Hash Move Score

  

**Evaluation Function**:

1. Material Evaluation

2. Piece Square Tables

3. Endgame Phase Weight

4. Pawn Evaluation

5. King and Pawn Shield Evaluation

6. Mop-Up Evaluation

7. Distance to Center Squares

  

## Openings with OBSIDIAN

  

OBSIDIAN uses the 'Titans.bin' Opening book, but feel free to swap it out with your own. Just update the code and 'make-exe.bat' accordingly.

  

## Best Game Played by OBSIDIAN (94.7% Accurency - Estimated Elo 2650 on Chess.com)

    [Event "60 Moves in 15 min"]
    [Site "Engine Match"]
    [Date "2023.10.03"]
    [Round "1"]
    [White "OBSIDIAN"]
    [Black "Nero"]
    [ECO "B84"]
    [Result "1-0"]
    1. e4 c5 2. Nf3 e6 3. Nc3 a6 4. d4 cxd4 5. Nxd4 Qc7 6. Be2 Nf6
    7. O-O d6 8. f4 Be7 9. Be3 O-O 10. g4 Re8 11. g5 Nfd7
    12. Bd3 e5 13. Nd5 Qc5 14. Nxe7+ Rxe7 15. Nf5 exf4 16. Nxe7+ Kf8
    17. Bxc5 Kxe7 18. Bd4 Kf8 19. Rxf4 Nc6 20. Bc4 Nd8 21. Bc3 Kg8
    22. Qxd6 b5 23. Bxf7+ Nxf7 24. Qd5 Kh8 25. Qxf7 Nf6 26. Qf8+ Ng8
    27. Bxg7# 1-0

  

## What OBSIDIAN Can't Do (Yet!)

  

- Occasionally behaves unpredictably with limited analysis time.

- Can be a bit slow sometimes.

  

## What's Next for OBSIDIAN

  

1. Smarter moves with NNUE.

2. Adding an Endgame Table for strategic play.

3. Speeding things up or considering a transition to C++.

  

## Join the Fun!

  

Explore the [chessprogramming wiki](https://www.chessprogramming.org/Main_Page) for ways to make OBSIDIAN even better. Your contributions are more than welcome!