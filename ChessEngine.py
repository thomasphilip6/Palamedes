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


def translateMovesToEngine(OriginalString=""):
    #we didn't se the same anotations for cells small 
    #letters in engine captal ones for moves
    newString= OriginalString.replace("A","a")
    newString= newString.replace("B","b")
    newString= newString.replace("C","c")
    newString= newString.replace("D","d")
    newString= newString.replace("E","e")
    newString= newString.replace("F","f")
    newString= newString.replace("G","g")
    newString= newString.replace("H","h")
    return newString

def translateEngineToMoves(OriginalString=""):
    print("Original win move:", OriginalString)
    newString= OriginalString.replace("a","A")
    newString= newString.replace("b","B")
    newString= newString.replace("c","C")
    newString= newString.replace("d","D")
    newString= newString.replace("e","E")
    newString= newString.replace("f","F")
    newString= newString.replace("g","G")
    newString= newString.replace("h","H")

    #that's to cut in half the string for moves
    startPos=newString[0:4//2]
    endPos=newString[4//2:] 
    print("Start move: ", startPos)
    print("end move: ", endPos)
    return startPos, endPos

def restartGame():
    baord.pop()

def updateEngineBoard(cell1,cell2):
    #we upadate with the player's move
    update = cell1+cell2 #the engine wants them on 1 string
    update=translateMovesToEngine(update)
    board.push_san(update)
    stockfish.set_fen_position(board.fen())#to send to stockfish the board
    print(board)


def getWinMove():
    bestMove= stockfish.get_best_move()
    board.push_san(bestMove)
    startPos, endPos = translateEngineToMoves(bestMove)
    print(board)

    return startPos, endPos




### try the game ###
"""
startGame()
getWinMove("a2", "a4")
print(board)
getWinMove("b1", "a3")
print(board)
"""