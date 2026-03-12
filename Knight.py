class Knight:
    
    def __init__(self):
        self.move_deltas = [
            (-2, -1), 
            (-2,  1),  
            (-1, -2),  
            (-1,  2),  
            ( 1, -2),  
            ( 1,  2),  
            ( 2, -1), 
            ( 2,  1)   
        ]
    
    def get_valid_moves(self, x, y, board):
        valid_moves = []
        for dx, dy in self.move_deltas:
            new_x = x + dx
            new_y = y + dy
            
            if board.is_valid_position(new_x, new_y) and not board.is_visited(new_x, new_y):
                valid_moves.append((new_x, new_y))
        
        return valid_moves
    
    def count_onward_moves(self, x, y, board):
        return len(self.get_valid_moves(x, y, board))
