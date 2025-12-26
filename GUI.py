from tkinter import ttk
import tkinter.font as tkfont

class gui():
    def __init__(self, root, engine=None):
        #In pattern: {Colour}, {Piece}
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
             ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
             ["__", "__", "__", "__", "__", "__", "__", "__"],
             ["__", "__", "__", "__", "__", "__", "__", "__"],
             ["__", "__", "__", "__", "__", "__", "__", "__"],
             ["__", "__", "__", "__", "__", "__", "__", "__"],
             ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
             ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        if engine is not None:
            self.engine = engine
            self.board = self.engine.board
        else:
            print("Engine is not present!")
            return

        self.piece_symbols = {"w": {"P": "\u2659", "N": "\u2658", "B": "\u2657", "R": "\u2656", "Q": "\u2655", "K": "\u2654"},
                              "b": {"P": "\u265F", "N": "\u265E", "B": "\u265D", "R": "\u265C", "Q": "\u265B", "K": "\u265A"}}
        
        self.update = False

        self.root = root

        root.title("Chess Engine (CE)")
        root.geometry("1500x1000")

        root.rowconfigure((0, 1, 2), weight=1)
        root.columnconfigure((1, 2), weight=1)

        self.create_widgets()
    

    def get_symbol(self, piece="_", colour="_"):
        if colour == "_":
            return ""
        
        try:
            return self.piece_symbols[colour][piece]
        except KeyError:
            return "?"
    

    def _update_board(self):
        for pos, button in enumerate(self.buttons):
            row = pos // 8
            column = pos % 8

            piece = self.board[row][column][1]
            colour = self.board[row][column][0]

            symbol = self.get_symbol(piece, colour)

            button.config(text=symbol)
        
        w_total = self.engine.TotalW
        b_total = self.engine.TotalB
        
        if w_total > b_total:
            self.labels[1].config(text=f"Player 1       +{w_total - b_total}")
            self.labels[0].config(text="Player 2")
        elif w_total == b_total:
            self.labels[1].config(text="Player 1")
            self.labels[0].config(text="Player 2")
        else:
            self.labels[0].config(text=f"Player 2       +{b_total - w_total}")
            self.labels[1].config(text="Player 1")
    

    def piece_clicked(self, var):
            self.engine.move_piece(var)
    

    def create_widgets(self):
        #Names
        label_font = tkfont.Font(font="Helvetica, 14 bold")
        
        label_style = ttk.Style(self.root)
        label_style.configure("Style.TLabel", font=label_font)

        self.labels = []

        p2_label = ttk.Label(self.root, text="Player 2", style="Style.TLabel")
        self.labels.append(p2_label)
        p2_label.grid(row=0, column=1)

        p1_label = ttk.Label(self.root, text="Player 1", style="Style.TLabel")
        self.labels.append(p1_label)
        p1_label.grid(row=2, column=1)

        #Board frame
        frame1 = ttk.Frame(self.root)
        for column in range(8):
            frame1.columnconfigure(column, weight=1, minsize=80)
        for row in range(8):
            frame1.rowconfigure(row, weight=1, minsize=80)
        
        #Inner frames (To make fixed size buttons)
        frames = []
        for i in range(64):
            row = i // 8
            column = i % 8

            my_frame = ttk.Frame(frame1)
            frames.append(my_frame)

            my_frame.grid(row=row, column=column, sticky="nesw")
        
        #Board Colours + Piece size
        self.piece_size = tkfont.Font(size=35)
        
        style_white = ttk.Style(self.root)
        style_white.configure("White.TButton", font=self.piece_size, background="#FFFFFF")

        style_green = ttk.Style(self.root)
        style_green.configure("Green.TButton", font=self.piece_size, background="#32a852")

        #8x8 Board
        self.buttons = []
        for i in range(64):
            row = i // 8
            column = i % 8

            piece = self.board[row][column][1]
            colour = self.board[row][column][0]

            symbol = self.get_symbol(piece, colour)

            style_c = "White.TButton"
            if (row + column) % 2 != 0:
                style_c = "Green.TButton"
            
            new_button = ttk.Button(frames[i], text=symbol, style=style_c, command= lambda var=i:self.piece_clicked(var))
            self.buttons.append(new_button)

            new_button.place(x=0, y=0, relwidth=1, relheight=1)
        
        frame1.grid(row=1, column=1)