#TODO Continue making the Anti-Chess Engine

import copy
from random import choice

class DumbBot():
    def __init__(self, engine=None):
        if engine is not None:
            self.engine = engine
            self.board = self.engine.board
        else:
            print("Engine is not present!")
            return
        self.all_positions = []

    
    def _validate_piece(self, board, square=0):
        piece = board[square // 8][square % 8]
            
        if piece == "__":
            return False
        if not self.engine.turn in piece:
            return False
            
        return True


    def get_positions(self, board_temp):
        board = copy.deepcopy(board_temp)
        
        self.engine._reset_able_sq()

        #3d list
        self.all_positions = []

        self.piece_pos = []

        for piece in range(64):
            if not self._validate_piece(board, piece):
                continue

            new_able_squares = self.engine.make_available_squares(piece, board)

            #Don't add any positions that don't move the piece
            flag = False
            for i in range(64):
                if new_able_squares[i // 8][i % 8] == 1:
                    flag = True
                    break
            
            if not flag:
                continue

            #Add each of the different positions that the bot can make
            for square in range(64):
                row = square // 8
                column = square % 8

                if new_able_squares[row][column] != 1:
                    continue

                new_position = copy.deepcopy(board)

                self.engine.selected_piece = board[piece // 8][piece % 8]
                self.engine.selected_piece_pos = piece

                temp = self.engine._make_move(square, new_position)
                if temp == -1:
                    continue
                new_position = copy.deepcopy(temp)

                
                #Validate move
                self.engine._reset_able_sq()

                self.engine._swap_turns()

                if self.engine.look_for_checks(new_position):
                    self.engine._swap_turns()
                    continue

                self.engine._swap_turns()

                
                self.all_positions.append(new_position)
                self.piece_pos.append((piece, square))
            
            self.engine._reset_able_sq()


    def make_move(self, board_temp=None):
        self.get_positions(board_temp)

        
        #Evalulate positions

        #1. Calculate total moves
        #(And pick the move that restricts itself the most)
        self.total_moves_ = []

        for position in self.all_positions: #Going through all of the positions
            position_total = 0

            for piece in range(64): #All the pieces
                if not self._validate_piece(position, piece):
                    continue

                available_squares = self.engine.make_available_squares(piece, position)

                #Looking through all the squares in available_squares to find how many are 1's
                for i in range(64):
                    if available_squares[i // 8][i % 8] == 1:
                        position_total += 1
            
            self.total_moves_.append(position_total)
        
        worst_pos_index = self.total_moves_.index(min(self.total_moves_))

        w_pos_values = self.piece_pos[worst_pos_index]

        self.engine._reset_able_sq()

        #"Selecting" piece
        self.engine.move_piece(w_pos_values[0])

        #Moving the piece
        self.engine.move_piece(w_pos_values[1])
        return
    

    def make_move_random(self, board_temp=None):
        self.get_positions(board_temp)
        
        self.engine._reset_able_sq()

        r_choice = choice(self.piece_pos)

        self.engine.move_piece(r_choice[0])
        self.engine.move_piece(r_choice[1])