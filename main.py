import tkinter as tk
import _tkinter as tk_error
import copy
from GUI import gui

class chess_engine():
    def __init__(self):
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                ["__", "__", "__", "__", "__", "__", "__", "__"],
                ["__", "__", "__", "__", "__", "__", "__", "__"],
                ["__", "__", "__", "__", "__", "__", "__", "__"],
                ["__", "__", "__", "__", "__", "__", "__", "__"],
                ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        
        w_king = False
        b_king = False
        for i in range(64):
            if self.board[i // 8][i % 8] == "wK":
                w_king = True
            elif self.board[i // 8][i % 8] == "bK":
                b_king = True
        
        if not (w_king and b_king):
            if not w_king:
                print("White King Missing!")
            if not b_king:
                print("Black King Missing!")
            root.destroy()
        
        self.last_position = []
        
        self.available_squares = [[0 for _ in range(8)] for _ in range(8)]

        self.en_passant = False
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
        self.selected_piece_pos = ""
        self.selected_piece = ""



    def _piece_value(self, piece):
            if piece in self.values:
                return self.values[piece]
            return 0
    

    def _swap_turns(self):
        if self.turn == "w":
            self.turn = "b"
            
        elif self.turn == "b":
            self.turn = "w"
 

    def check_total(self):
        self.TotalW = 0
        self.TotalB = 0

        for row, item in enumerate(self.board):
            for column, item2 in enumerate(item):
                if self.board[row][column][0] == "w":
                    self.TotalW += self._piece_value(item2[1])
                elif self.board[row][column][0] == "b":
                    self.TotalB += self._piece_value(item2[1])

    
    def _set_available_sq(self, capture, var, board=None, row_sub=0, col_sub=0, rook=False, bishop=False):
        if board is None:
            board=self.board
        
        if not (rook or bishop):
            try:
                row_to_change = (var // 8) - row_sub
                col_to_change = (var % 8) - col_sub
                piece_change = board[row_to_change][col_to_change]

                #Check if trying to reach beyond the board. Take this part out if you want wrap around chess ;)
                if row_to_change > 7 or row_to_change < 0:
                    return
                if col_to_change > 7 or col_to_change < 0:
                    return

                #Checks if pieces of the same colour is in the way
                if "w" in self.selected_piece and "w" in piece_change:
                    return
                elif "b" in self.selected_piece and "b" in piece_change:
                    return
            
                #Pawn capturing diagonaly
                if capture:
                    if self.en_passant:
                        self.available_squares[row_to_change - 1][col_to_change] = 1
                        self.available_squares[row_to_change][col_to_change] = 2
                        return
                   
                    if "w" in self.selected_piece and "b" in piece_change:
                        self.available_squares[row_to_change][col_to_change] = 1
                    
                    elif "b" in self.selected_piece and "w" in piece_change:
                        self.available_squares[row_to_change][col_to_change] = 1
            
                #Checks if a piece is infront of a pawn
                if self.selected_piece == "wP" and "b" in piece_change:
                    return
                elif self.selected_piece == "bP" and "w" in piece_change:
                    return

                self.available_squares[row_to_change][col_to_change] = 1
            except IndexError:
                return
            return


        #If rook or bishop
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
                    if "w" in board[row][column]:
                        break
                        
                    #If an enemy piece is in the way, make it capturable
                    elif "b" in board[row][column]:
                        self.available_squares[row][column] = 1
                        break
                    
                if "b" in self.selected_piece:
                    #If the same coloured piece is in the way, stop going this direction
                    if "b" in board[row][column]:
                        break

                    #If an enemy piece is in the way, make it capturable
                    elif "w" in board[row][column]:
                        self.available_squares[row][column] = 1
                        break

                self.available_squares[row][column] = 1
    

    #Pins and illegial move checking both work from this!
    def look_for_checks(self, board=None):
        if board is None:
            board = self.board

        def _king_in_check(multiplier=1):
            self.make_available_squares(piece, board)

            row = piece // 8
            column = piece % 8

            if "P" in board[row][column]:
                #Get rid of the squares infront of the pawn since they can't capture forwards
                self.available_squares[row + multiplier][column] = 0
                try:
                    self.available_squares[row + (2 * multiplier)][column] = 0
                except IndexError:
                    pass

            #Check all of the available squares and check if any intersect the king's position
            for i in range(64):
                row_sq = i // 8
                col_sq = i % 8

                if self.available_squares[row_sq][col_sq] == 1 and "K" in board[row_sq][col_sq]:
                    return True
            return False
            
            
        #Looks at all the squares that each piece is targeting
        for piece in range(64):
            self._reset_able_sq()
            
            #Filtering out all empty squares
            if board[piece // 8][piece % 8] == "__":
                continue

            #Black last moved a piece, look if white's king is in check
            if self.turn == "b" and "b" in board[piece // 8][piece % 8]:
                if _king_in_check():
                    return True
                
            #White last moved a piece, look if black's king is in check
            if self.turn == "w" and "w" in board[piece // 8][piece % 8]:
                if _king_in_check(-1):
                    return True
        return False
    

    def look_for_checkmate(self):
        self._reset_able_sq()

        #3D List
        positions_to_check = []

        #Swap turns to find all the moves for the next player
        self._swap_turns()

        #Check every piece
        for piece in range(64):
            if self.board[piece // 8][piece % 8] == "__":
                continue
            elif not self.turn in self.board[piece // 8][piece % 8]:
                continue
            
            self.make_available_squares(piece)

            #Check every move for that piece
            for move in range(64):
                new_pos = []
                
                if self.available_squares[move // 8][move % 8] != 1:
                    continue
                
                new_pos = copy.deepcopy(self.board)

                row = self.selected_piece_pos // 8
                column = self.selected_piece_pos % 8
            
                new_pos[row][column] = "__"

                #Pawn promotion or not?
                if move // 8 == 0 and self.selected_piece == "wP":
                    new_pos[move // 8][move % 8] = "wQ"
                elif move // 8 == 7 and self.selected_piece == "bP":
                    new_pos[move // 8][move % 8] = "bQ"
                else:
                    new_pos[move // 8][move % 8] = self.selected_piece
                
                try:
                    if self.available_squares[(move // 8) + 1][move % 8] == 2:
                        self.board[(move // 8) + 1][move % 8] = "__"
                except IndexError:
                    pass
                
                #Add the new position to be checked
                positions_to_check.append(new_pos)
            
            self._reset_able_sq()
        
        self._swap_turns()

        for i in positions_to_check:
            if not self.look_for_checks(i):
                return False
        
        self._swap_turns()
        return True

    
    def _revert_position(self):
        self.board = self.last_position
        chess_gui.board = self.last_position

        self.last_position = []

        self._reset_able_sq()
        return
    

    def make_available_squares(self, var, board=None):
        if board is None:
            board = self.board
        
        self._reset_able_sq()
        
        piece = board[var // 8][var % 8]

        self.selected_piece = piece
        self.selected_piece_pos = var

        if "P" in piece:
            def set_diagonal(row_sub, col_sub, colour):
                try:
                    if colour in board[(var // 8) - row_sub][(var % 8) - col_sub]:
                        self._set_available_sq(True, var, board, row_sub, col_sub)
                except IndexError:
                    return
            

            def en_passant(col_sub, colour):
                try:
                    self.en_passant = False

                    if board[(var // 8)][(var % 8) - col_sub] == colour:
                        if self.last_position[(var // 8) - 2][(var % 8) - col_sub] == colour:
                            self.en_passant = True
                            self._set_available_sq(True, var, board, 0, col_sub)
                except IndexError:
                    return
                self.en_passant = False
                return
            

            if "w" in piece:
                self._set_available_sq(False, var, board, 1) #1 square up
                if var // 8 == 6: #2nd rank
                    self._set_available_sq(False, var, board, 2) #2 squares ups

                set_diagonal(1, 1, "b") #1 up, 1 left
                set_diagonal(1, -1, "b") #1 up, 1 right

                en_passant(-1, "bP")
                en_passant(1, "bP")
            
            elif "b" in piece:
                self._set_available_sq(False, var, board, -1) #1 square "down"
                if var // 8 == 1: #8th rank
                    self._set_available_sq(False, var, board, -2) #2 squares "down"
                
                set_diagonal(-1, 1, "w") #1 "down", 1 left
                set_diagonal(-1, -1, "w") #1 "down", 1 right

                en_passant(-1, "wP")
                en_passant(1, "wP")
        
        elif "N" in piece:
            self._set_available_sq(False, var, board, 2, 1) #2 up, 1 left
            self._set_available_sq(False, var, board, 2, -1) #2 up, 1 right
            self._set_available_sq(False, var, board, 1, 2) #1 up, 2 left
            self._set_available_sq(False, var, board, -1, 2) #1 down, 2 left
            self._set_available_sq(False, var, board, -2, 1) #2 down, 1 left
            self._set_available_sq(False, var, board, -2, -1) #2 down, 1 right
            self._set_available_sq(False, var, board, -1, -2) #1 down, 2 right
            self._set_available_sq(False, var, board, 1, -2) #1 up, 2 right
        
        elif "B" in piece:
            self._set_available_sq(False, var, board, 0, 0, False, True)
        
        elif "R" in piece:
            self._set_available_sq(False, var, board, 0, 0, True)
        
        elif "Q" in piece:
            self._set_available_sq(False, var, board, 0, 0, False, True)
            self._set_available_sq(False, var, board, 0, 0, True)
        
        elif "K" in piece:
            for row in range(1, -2, -1):
                for column in range(1, -2, -1):
                    if row == 0 and column == 0:
                        continue
                    self._set_available_sq(False, var, board, row, column)
    

    def move_piece(self, var, board=None):
        if board is None:
            board = self.board
        
        #Actually moving a piece
        if self.selected_piece != "":
            row = self.selected_piece_pos // 8
            column = self.selected_piece_pos % 8

            #Checks if a piece is trying to move to a square that it can't
            if self.available_squares[var // 8][var % 8] != 1:
                self.selected_piece_pos = ""
                self.selected_piece = ""
                return
            
            #Saving the last position to check for illegial moves
            self.last_position = copy.deepcopy(self.board)
            
            board[row][column] = "__"

            #Pawn promotion or not?
            if var // 8 == 0 and self.selected_piece == "wP":
                board[var // 8][var % 8] = "wQ"
            elif var // 8 == 7 and self.selected_piece == "bP":
                board[var // 8][var % 8] = "bQ"
            else:
                board[var // 8][var % 8] = self.selected_piece

            try:
                if self.available_squares[(var // 8) + 1][var % 8] == 2:
                    self.board[(var // 8) + 1][var % 8] = "__"
            except IndexError:
                pass
            
            self.selected_piece_pos = ""
            self.selected_piece = ""

            next_turn = "w"
            if self.turn == "w":
                next_turn = "b"

            #233-246 If anyone if currently in check, undo the move if it's illegial
            def in_check():
                self._swap_turns()

                if self.look_for_checks():
                    self._swap_turns()
                    self._revert_position()
                    return
            
            if self.w_in_check and self.turn == "w":
                in_check()
                return
            elif self.b_in_check and self.turn == "b":
                in_check()
                return

            if self.look_for_checks():
                #Checking for "b" cause it means that when the turns are swapped, the current turn will be white's
                if self.turn == "b":
                    self.w_in_check = True
                else:
                    self.b_in_check = True

                if self.look_for_checkmate():
                    print("Checkmate!")
            
            #Unchecks current player if not in check
            if self.w_in_check is False and self.turn == "w":
                self.w_in_check = False
            elif self.b_in_check is False and self.turn == "b":
                self.b_in_check = False
            
            self.turn = next_turn
            chess_gui.board = board
            self.board = board
            self._reset_able_sq()
            return
        
        #Finding the available squares that a piece can move to
        self._reset_able_sq()

        if not self.turn in board[var // 8][var % 8]:
            return

        if board[var // 8][var % 8] == "__":
            return

        self.make_available_squares(var)


if __name__ == "__main__":
    root = tk.Tk()
    engine = chess_engine()

    try:
        chess_gui = gui(root, engine)
    except tk_error.TclError:
        pass

    root.mainloop()