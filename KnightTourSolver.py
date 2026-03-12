from Heuristics import Heuristics


class KnightTourSolver:
    
    def __init__(self, board, knight):
        self.board = board
        self.knight = knight
        self.stats = {
            'steps': 0,        
            'backtracks': 0    
        }
    
    def reset_stats(self):
        self.stats['steps'] = 0
        self.stats['backtracks'] = 0
    
    def solve_basic(self, x, y, move_number):
        self.stats['steps'] += 1
        self.board.mark_visited(x, y, move_number)
        
        if move_number == 63:
            return True
        
        # Obtenir tous les successeurs valides
        valid_moves = self.knight.get_valid_moves(x, y, self.board)
    
      
        for next_x, next_y in valid_moves:
            if self.solve_basic(next_x, next_y, move_number + 1):
                return True
            self.stats['backtracks'] += 1
        
        self.board.unmark_visited(x, y)
        return False
    
    def solve_enhanced(self, x, y, move_number):
        self.stats['steps'] += 1
        self.board.mark_visited(x, y, move_number)
        
        if move_number == 63:
            return True
        
        
        valid_moves = self.knight.get_valid_moves(x, y, self.board)

        valid_moves = Heuristics.MRV_LCV_combined(valid_moves, self.knight, self.board)
        
       
        for next_x, next_y in valid_moves:
            if self.solve_enhanced(next_x, next_y, move_number + 1):
                return True
            self.stats['backtracks'] += 1
        
        self.board.unmark_visited(x, y)
        return False