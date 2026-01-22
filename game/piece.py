class Piece:
    def __init__(self,col,row,symbol):
        self.col = col
        self.row = row
        self.symbol = symbol
        if(symbol==symbol.lower()):
            self.color = "black"
        else:
            self.color = "white"
    def __str__(self):
        return f"Piece {self.type} {self.color} {self.col} {self.row}"
