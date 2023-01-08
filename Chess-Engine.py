import chess
#import chess.engine 
from stockfish import Stockfish

#engine = chess.engine.SimpleEngine.popen_uci(r"Z:\Git-pal\Palamedes\data\chessEngine\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe")
"""
stockfish=Stockfish(path="Z:\Git-pal\Palamedes\data\chessEngine\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe")
stockfish.set_depth(20)#How deep the AI looks
stockfish.set_skill_level(20)#Highest rank stockfish
print(stockfish.get_parameters())
"""
"""
board = chess.Board()

board.push_san("d2d4")
stockfish.set_fen_position(board.fen())#to send to stockfish the board
print(stockfish.get_best_move())
print(board)
"""

def startGame():

    global stockfish
    stockfish=Stockfish(path="Z:\Git-pal\Palamedes\data\chessEngine\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe")
    stockfish.set_depth(20)#How deep the AI looks
    stockfish.set_skill_level(20)#Highest rank stockfish


    global board
    board = chess.Board()


def restartGame():
    baord.pop()


def getWinMove(cell1,cell2):

    #first we upadate with the player's move
    board.push_san(cell1+cell2)
    stockfish.set_fen_position(board.fen())#to send to stockfish the board
    bestMove= stockfish.get_best_move()
    board.push_san(bestMove)

    return bestMove




### try the game ###

startGame()
getWinMove("a2", "a4")
print(board)
getWinMove("b1", "a3")
print(board)
