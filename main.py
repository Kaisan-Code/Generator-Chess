#TODO Make stalemate detection

import tkinter as tk
import _tkinter as tk_error
import copy
from GUI import gui
from Bot import DumbBot

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
        
        wKing = False
        bKing = False

        #Reduced range from 64 to 8 - only need to check the 8 rows.
        for i in range(8):
            if "wK" in self.board[i]:
                wKing = True
            elif "bK" in self.board[i]:
                bKing = True
        
        if not (wKing and bKing):
            if not wKing:
                print("White King Missing!")
            if not bKing:
                print("Black King Missing!")
            root.destroy()
        
        self.last_position = []
        
        self.available_squares = [[0 for _ in range(8)] for _ in range(8)]

        self.en_passant = False
        self.turn = "w"
        self.w_in_check = False
        self.b_in_check = False

        #Left rook, King, Right rook (From white's POV)
        self.castle_rights_w = [True, True, True]
        self.castle_rights_b = [True, True, True]
        
        #White, Black
        self.can_castle = [True, True]

        for i in range(64):
            if self.board[i // 8][i % 8] == "wK":
                if i != 60:
                    self.w_can_castle = False
            elif self.board[i // 8][i % 8] == "bK":
                if i != 4:
                    self.b_can_castle = False

        self.TotalW = 39
        self.TotalB = 39
        self.checkmate = False
        self.values = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9}
        self.selected_piece = ""
        self.selected_piece_pos = ""
        
        self.dumb_bot = DumbBot(self)
    

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

                #Checks if a piece of the same colour is on the square to change
                for colour in ["w", "b"]:
                    if colour in self.selected_piece and colour in piece_change:
                        return
            
                #Pawn capturing diagonaly
                if capture:
                    if self.en_passant:
                        up_or_down = 1
                        if "b" in self.selected_piece:
                            up_or_down = -1
                        
                        self.available_squares[row_to_change - up_or_down][col_to_change] = 1
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

                colour = self.selected_piece[0]
                emyColour = "w"
                if colour == "w":
                    emyColour = "b"

                #If the same coloured piece is in the way, stop going this direction
                if colour in board[row][column]:
                    break
                        
                #If an enemy piece is in the way, make it capturable
                elif emyColour in board[row][column]:
                    self.available_squares[row][column] = 1
                    break

                self.available_squares[row][column] = 1
    

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

            for i in range(64):
                row_sq = i // 8
                col_sq = i % 8

                #If one of the available squares are intersecting the King's position, return True
                if self.available_squares[row_sq][col_sq] == 1 and "K" in board[row_sq][col_sq]:
                    return True
            #If no move attacks the King, then no check (for this piece)
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
            elif self.turn == "w" and "w" in board[piece // 8][piece % 8]:
                if _king_in_check(-1):
                    return True
        return False
    

    def look_for_checkmate(self):
        self._reset_able_sq()

        #Swap turns to find all the moves for the next player
        self._swap_turns()

        #Check every piece
        for piece in range(64):
            if self.board[piece // 8][piece % 8] == "__":
                continue
            elif not self.turn in self.board[piece // 8][piece % 8]:
                continue
            
            able_sq = self.make_available_squares(piece)
            select_piece = self.selected_piece
            select_piece_pos = self.selected_piece_pos

            #Check every move for that piece
            for square in range(64):
                new_pos = []

                self.selected_piece = select_piece
                self.selected_piece_pos = select_piece_pos
                
                if able_sq[square // 8][square % 8] != 1:
                    continue
                
                #Copying the board to not change the actual board state
                new_pos = copy.deepcopy(self.board)
                
                new_pos = self._make_move(square, new_pos)
                if new_pos == -1:
                    continue

                self._swap_turns()
                
                if not self.look_for_checks(new_pos):
                    #Check if it's actually moving a piece
                    #Aka if the available_squares has a 1 in it
                    flag = False
                    
                    for i in range(8):
                        if 1 in able_sq[i]:
                            flag = True
                    
                    if flag:
                        return False
                
                self._swap_turns()
            
            self._reset_able_sq()
        return True
    

    def look_for_stalemate(self, board=None):
        if board is None:
            board = self.board
        



    def _make_move(self, var, board=None, castle_rights_=False):
        if board is None:
            board = self.board
        
        r = var // 8
        c = var % 8

        select_p_r = self.selected_piece_pos // 8
        select_p_c = self.selected_piece_pos % 8

        board[select_p_r][select_p_c] = "__"


        #Pawn promotion or not?
        if var // 8 == 0 and self.selected_piece == "wP":
            board[var // 8][var % 8] = "wQ"
        elif var // 8 == 7 and self.selected_piece == "bP":
            board[var // 8][var % 8] = "bQ"
        else:
            board[var // 8][var % 8] = self.selected_piece


        try:
            up_or_down = -1
            if self.selected_piece == "wP":
                up_or_down = 1

            #The pawn that would be captured via en pssant
            if self.available_squares[(var // 8) + up_or_down][var % 8] == 2:
                board[(var // 8) + up_or_down][var % 8] = "__"
        except IndexError:
            pass

        
        #Looking if the King is moving "through" check while castling
        if abs(self.selected_piece_pos - var) == 2 and "K" in self.selected_piece:
            new_board = copy.deepcopy(board)
            
            #Where it just placed a King
            new_board[r][c] = "__"
                
            #Place that the King would be if it moved only one square
            if var > self.selected_piece_pos:
                new_board[r][c - 1] = self.selected_piece
            else:
                new_board[r][c + 1] = self.selected_piece
            
            self._swap_turns()

            copy_selected_piece = self.selected_piece
            copy_selected_piece_pos = self.selected_piece_pos
                
            if self.look_for_checks(new_board):
                self._swap_turns()

                self.selected_piece = copy_selected_piece
                self.selected_piece_pos = copy_selected_piece_pos
                return -1
            self._swap_turns()
            self.selected_piece = copy_selected_piece
            self.selected_piece_pos = copy_selected_piece_pos

        #Making a copy in case we don't actually want to change the castle rights (look_for_checkmate())
        copy_castle_r_w = self.castle_rights_w[:]
        copy_castle_r_b = self.castle_rights_b[:]

        #Castling rights
        if self.selected_piece == "wR":
            #Bottom left corner
            if self.selected_piece_pos == 56:
                copy_castle_r_w[0] = False
            #Bottom right corner
            elif self.selected_piece_pos == 63:
                copy_castle_r_w[2] = False
                
            #Capturing black's rook
            elif var == 0:
                copy_castle_r_b[0] = False
            elif var == 7:
                copy_castle_r_b[2] = False
            
        elif self.selected_piece == "bR":
            #Top left corner
            if self.selected_piece_pos == 0:
                copy_castle_r_b[0] = False
            #Top right corner
            elif self.selected_piece_pos == 7:
                copy_castle_r_b[2] = False
            
            #Capturing white's rook
            elif var == 56:
                copy_castle_r_w[0] = False
            elif var == 63:
                copy_castle_r_w[2] = False

        #If the King is moving, remove its castling rights
        if self.selected_piece_pos == 60 and self.selected_piece == "wK":
            copy_castle_r_w[1] = False
                
        elif self.selected_piece_pos == 4 and self.selected_piece == "bK":
            copy_castle_r_b[1] = False
            
        def move_rook(castle_row, piece, num):
            #Num is the start square of the King
            if not self.selected_piece_pos == num:
                return
            
            if not "K" in self.selected_piece:
                return

            if var == (num + 2):
                board[castle_row][7] = "__"
                board[castle_row][5] = piece
                
            if var == (num - 2):
                board[castle_row][0] = "__"
                board[castle_row][3] = piece
        
        #If we want to change the castle rights (move_piece())
        if castle_rights_:
            self.castle_rights_w = copy_castle_r_w[:]
            self.castle_rights_b = copy_castle_r_b[:]

        move_rook(7, "wR", 60) #Move white's rook
        move_rook(0, "bR", 4) #Move black's rook
        return board

    
    def _revert_position(self):
        self.board = self.last_position
        chess_gui.board = self.last_position

        #Reseting the castle rights
        self.castle_rights_w = self.last_w_castle_rights
        self.castle_rights_b = self.last_b_castle_rights
        self.can_castle = self.last_can_castle

        self.last_position = []
        self.last_can_castle = []
        self.last_w_castle_rights = []
        self.last_b_castle_rights = []

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
                row = var // 8
                col = var % 8

                try:
                    #Checks if an enemy piece is on a diagonal (from the pawn)
                    if colour in board[row - row_sub][col - col_sub]:
                        self._set_available_sq(True, var, board, row_sub, col_sub)
                except IndexError:
                    return
            

            def en_passant(col_sub, colour):
                try:
                    self.en_passant = False

                    row = var // 8
                    col = var % 8

                    #Checks if a piece (of colour) is next to it
                    if board[row][col - col_sub] == colour:
                        up_or_down = -2
                        if colour == "bP":
                            up_or_down = 2
                        
                        if self.last_position[row - up_or_down][col - col_sub] == colour:
                            #Checking if the pawn is in the right row
                            #And if it's the right colour of pawn
                            #"colour" would be the enemy colour, not the piece's colour
                            working_pairs = [("bP", 3), ("wP", 4)]
                            
                            if (colour, row) in working_pairs:
                                self.en_passant = True
                                self._set_available_sq(True, var, board, 0, col_sub)
                except IndexError:
                    return
                self.en_passant = False
                return
            
            
            if "w" in piece:
                self._set_available_sq(False, var, board, 1)

                if var // 8 == 6:
                    if board[(var // 8) - 1][var % 8] == "__":
                        self._set_available_sq(False, var, board, 2)
                
                set_diagonal(1, 1, "b")
                set_diagonal(1, -1, "b")

                en_passant(-1, "bP")
                en_passant(1, "bP")
            
            elif "b" in piece:
                self._set_available_sq(False, var, board, -1)

                if var // 8 == 1:
                    if board[(var // 8) + 1][var % 8] == "__": #Remove to have pawns "teleport" through other pieces ;)
                        self._set_available_sq(False, var, board, -2)
                
                set_diagonal(-1, 1, "w")
                set_diagonal(-1, -1, "w")

                en_passant(-1, "wP")
                en_passant(1, "wP")
        
        elif "N" in piece:
            #Hard-Coding the Knight movements
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
            def _castle_movements(can_castle, castle_rights, num):
                #Num is the start square of the King (before castling)
                if can_castle is False:
                    return

                if castle_rights[0] and board[num // 8][(num % 8) - 1] == "__":
                    #2 Squares to the left
                    self._set_available_sq(False, var, board, 0, 2)
                
                if castle_rights[2] and board[num // 8][(num % 8) + 1] == "__":
                    #2 Squares to the right
                    self._set_available_sq(False, var, board, 0, -2)
                return
            

            for row in range(1, -2, -1):
                for column in range(1, -2, -1):
                    if row == 0 and column == 0:
                        continue
                    self._set_available_sq(False, var, board, row, column)
            
            if self.castle_rights_w[1] is False:
                self.w_can_castle = False
                self.can_castle[0] = False
            
            if self.castle_rights_b[1] is False:
                self.b_can_castle = False
                self.can_castle[1] = False

            if self.turn == "w":
                _castle_movements(self.can_castle[0], self.castle_rights_w, 60)
            else:
                _castle_movements(self.can_castle[1], self.castle_rights_b, 4)
        return self.available_squares
    

    #This is the function to make the move
    def move_piece(self, var, board=None):
        if board is None:
            board = self.board
        
        #The row and column that will be changed
        #OR the row and column of the selected piece (see not moving a piece)
        row = var // 8
        col = var % 8
        
        #Actually moving a piece
        if self.selected_piece != "":
            #Checks if a piece is trying to move to a square that it can't
            if self.available_squares[row][col] != 1:
                self.selected_piece_pos = ""
                self.selected_piece = ""
                return
            
            #Saving the last position to check for illegial moves
            #And saving the castling rights in case of illegial move
            
            #Replaces the use of deepcopying the whole board
            self.last_position = [self.board[i][:] for i in range(8)]

            self.last_w_castle_rights = self.castle_rights_w[:]
            self.last_b_castle_rights = self.castle_rights_b[:]
            self.last_can_castle = self.can_castle[:]

            changed_board = self._make_move(var, self.board, True)
            
            if changed_board == -1:
                self._reset_able_sq()
                return
            
            self.board = changed_board
            
            self.selected_piece_pos = ""
            self.selected_piece = ""

            next_turn = "w"
            if self.turn == "w":
                next_turn = "b"

            #Undoing move if it moves into check
            #MOVING INTO CHECK
            self._swap_turns()
            
            if self.look_for_checks():
                self._revert_position()
                self._swap_turns()
                return
            
            self._swap_turns()

            
            if self.look_for_checkmate():
                print("Checkmate!")
                self.checkmate = True
            #look_for_checkmate swaps the turns, so no need to do it again

            
            #Updating board(s)
            self.turn = next_turn
            self.check_total()
            chess_gui.board = board
            self.dumb_bot.board = board
            self.board = board
            self._reset_able_sq()
            chess_gui._update_board()

            if self.checkmate:
                print(self.board)
                return
            if self.turn == "b":
                root.after(500, lambda: self.dumb_bot.make_move_random(self.board))
            return


        #Finding the available squares that a piece can move to
        self._reset_able_sq()

        if not self.turn in board[row][col]:
            return

        if board[row][col] == "__":
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