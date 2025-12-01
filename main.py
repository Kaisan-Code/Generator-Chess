#TODO Make checks work
#TODO Make pins work
#TODO Find and show checkmate

import tkinter as tk
from GUI import gui

class chess_engine():
    def __init__(self, root):
        #In pattern: {Colour}, {Piece}
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
             ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
             ["__", "__", "__", "__", "__", "__", "__", "__"],
             ["__", "__", "__", "__", "__", "__", "__", "__"],
             ["__", "__", "__", "__", "__", "__", "__", "__"],
             ["__", "__", "__", "__", "__", "__", "__", "__"],
             ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
             ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        
        self.last_position = []
        
        self.available_squares = [[0 for _ in range(8)] for _ in range(8)]

        self.turn = "w"
        self.w_in_check = False
        self.b_in_check = False
        self.TotalW = 39
        self.TotalB = 39
        self.values = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9}
        self.selected_piece = ""
        self.selected_piece_pos = ""
    

    def _reset_able_sq(self):
        self.available_squares = [[0 for _ in range(8)] for _ in range(8)]
    

    def get_symbol(self, piece="_", colour="_"):
        if colour == "_":
            return ""
        
        try:
            return self.piece_symbols[colour][piece]
        except KeyError:
            return "?"


    def _piece_value(self, piece):
            if piece in self.values:
                return self.values[piece]
            return 0
 

    def check_total(self):
        self.TotalW = 0
        self.TotalB = 0

        for row, item in enumerate(self.board):
            for column, item2 in enumerate(item):
                if self.board[row][column][0] == "w":
                    self.TotalW += self._piece_value(item2[1])
                elif self.board[row][column][0] == "b":
                    self.TotalB += self._piece_value(item2[1])

    
    def _set_available_sq(self, capture, var, row_sub=0, col_sub=0, rook=False, bishop=False):
        if rook or bishop:
            directions = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
            
            if rook:
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            
            #Making the rook/bishop squares
            for value in directions:
                for j in range(1, 8):
                    row = (var // 8) + (value[0] * j)
                    column = (var % 8) + (value[1] * j)

                    if row > 7 or row < 0:
                        continue
                    if column > 7 or column < 0:
                        continue

                    #Check if any pieces are in the way
                    if "w" in self.selected_piece:
                        #If the same coloured piece is in the way, stop going this direction
                        if "w" in self.board[row][column]:
                            break
                        
                        #If an enemy piece is in the way, make it capturable
                        elif "b" in self.board[row][column]:
                            self.available_squares[row][column] = 1
                            break
                    
                    if "b" in self.selected_piece:
                        #If the same coloured piece is in the way, stop going this direction
                        if "b" in self.board[row][column]:
                            break

                        #If an enemy piece is in the way, make it capturable
                        elif "w" in self.board[row][column]:
                            self.available_squares[row][column] = 1
                            break

                    self.available_squares[row][column] = 1

        try:
            row_to_change = (var // 8) - row_sub
            col_to_change = (var % 8) - col_sub
            piece_change = self.board[row_to_change][col_to_change]

            #Checks if pieces of the same colour is in the way
            if "w" in self.selected_piece and "w" in piece_change:
                return
            elif "b" in self.selected_piece and "b" in piece_change:
                return
            
            #Pawn capturing diagonaly
            if capture:
                if "w" in self.selected_piece and "b" in piece_change:
                    self.available_squares[row_to_change][col_to_change] = 1
                elif "b" in self.selected_piece and "w" in piece_change:
                    self.available_squares[row_to_change][col_to_change] = 1
            
            #Checks if a piece is infront of a pawn
            if "P" in self.selected_piece and "b" in piece_change:
                return

            self.available_squares[row_to_change][col_to_change] = 1
        except IndexError:
            return
    

    def look_for_checks(self, var):
            pass
    

    def move_piece(self, var, look_for_check=False):
        #Actually moving a piece
        if self.selected_piece != "":
            row = self.selected_piece_pos // 8
            column = self.selected_piece_pos % 8

            if self.available_squares[var // 8][var % 8] != 1:
                self.selected_piece_pos = ""
                self.selected_piece = ""
                return
            
            #Saving the last position to check for illegial moves
            self.last_position = self.board
            
            self.board[row][column] = "__"

            #Pawn promotion or not?
            if var // 8 == 0 and self.selected_piece == "wP":
                self.board[var // 8][var % 8] = "wQ"
            elif var // 8 == 7 and self.selected_piece == "bP":
                self.board[var // 8][var % 8] = "bQ"
            else:
                self.board[var // 8][var % 8] = self.selected_piece
            
            self.w_in_check = False
            self.b_in_check = False

            self.selected_piece_pos = ""
            self.selected_piece = ""

            gui.board = self.board
            self._reset_able_sq()

            if self.turn == "w":
                self.turn = "b"
            
            elif self.turn == "b":
                self.turn = "w"

            self.look_for_checks(var)
            return
        
        #Finding the available squares that a piece can move to
        self._reset_able_sq()

        piece = self.board[var // 8][var % 8]

        if not self.turn in piece:
            return

        if piece == "__":
            return
        
        self.selected_piece = piece
        self.selected_piece_pos = var

        if "P" in piece:
            if "w" in piece:
                self._set_available_sq(False, var, 1) #1 square up
                if var // 8 == 6: #2nd rank
                    self._set_available_sq(False, var, 2) #2 squares up
                
                self._set_available_sq(True, var, 1, 1) #1 up, 1 left
                self._set_available_sq(True, var, 1, -1) #1 up, 1 right
            
            elif "b" in piece:
                self._set_available_sq(False, var, -1) #1 square "down"
                if var // 8 == 1: #8th rank
                    self._set_available_sq(False, var, -2) #2 squares "down"
                
                self._set_available_sq(True, var, -1, 1) #1 "down", 1 left
                self._set_available_sq(True, var, -1, -1) #1 "down", 1 right
        
        elif "N" in piece:
            self._set_available_sq(False, var, 2, 1) #2 up, 1 left
            self._set_available_sq(False, var, 2, -1) #2 up, 1 right
            self._set_available_sq(False, var, 1, 2) #1 up, 2 left
            self._set_available_sq(False, var, -1, 2) #1 down, 2 left
            self._set_available_sq(False, var, -2, 1) #2 down, 1 left
            self._set_available_sq(False, var, -2, -1) #2 down, 1 right
            self._set_available_sq(False, var, -1, -2) #1 down, 2 right
            self._set_available_sq(False, var, 1, -2) #1 up, 2 right
        
        elif "B" in piece:
            self._set_available_sq(False, var, 0, 0, False, True)
        
        elif "R" in piece:
            self._set_available_sq(False, var, 0, 0, True)
        
        elif "Q" in piece:
            self._set_available_sq(False, var, 0, 0, False, True)
            self._set_available_sq(False, var, 0, 0, True)
        
        elif "K" in piece:
            for row in range(1, -2, -1):
                for column in range(1, -2, -1):
                    if row == 0 and column == 0:
                        continue
                    self._set_available_sq(False, var, row, column)


if __name__ == "__main__":
    root = tk.Tk()
    engine = chess_engine(root)
    chess_gui = gui(root, engine)
    root.mainloop()