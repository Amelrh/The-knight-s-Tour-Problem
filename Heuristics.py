class Heuristics:
    
    @staticmethod
    def MRV(moves, knight, board):
        if not moves:
            return moves
        
        moves_with_degree = [
            (move, knight.count_onward_moves(move[0], move[1], board))
            for move in moves
        ]
        
        
        moves_with_degree.sort(key=lambda x: x[1])
        
        
        return [move for move, degree in moves_with_degree]
    
    @staticmethod
    def LCV(moves, knight, board):
        if not moves:
            return moves
        degree_cache = {}
        
        for move in moves:
            x, y = move
    
            if move not in degree_cache:
                degree_cache[move] = knight.count_onward_moves(x, y, board)
            
            for dx, dy in knight.move_deltas:
                nx, ny = x + dx, y + dy
                neighbor = (nx, ny)
                
                if (board.is_valid_position(nx, ny) and 
                    not board.is_visited(nx, ny) and
                    neighbor not in degree_cache):
                   
                    degree_cache[neighbor] = knight.count_onward_moves(nx, ny, board)
        
        
        def lcv_score(pos):
            x, y = pos
            total_freedom = 0
            
            # Sommer les degrés des voisins 
            for dx, dy in knight.move_deltas:
                nx, ny = x + dx, y + dy
                neighbor = (nx, ny)
                
                if (board.is_valid_position(nx, ny) and 
                    not board.is_visited(nx, ny)):
                    
                    total_freedom += degree_cache.get(neighbor, 0)
            
            return -total_freedom
        
       
        return sorted(moves, key=lcv_score)
    
    @staticmethod
    def MRV_LCV_combined(moves, knight, board):
        if not moves:
            return moves
        degree_cache = {}
        
        for move in moves:
            x, y = move
            if move not in degree_cache:
                degree_cache[move] = knight.count_onward_moves(x, y, board)
            
            for dx, dy in knight.move_deltas:
                nx, ny = x + dx, y + dy
                neighbor = (nx, ny)
                if (board.is_valid_position(nx, ny) and 
                    not board.is_visited(nx, ny) and
                    neighbor not in degree_cache):
                    degree_cache[neighbor] = knight.count_onward_moves(nx, ny, board)
        
        def combined_score(pos):
            x, y = pos
            mrv_score = degree_cache.get(pos, 0)
            
            total_freedom = 0
            for dx, dy in knight.move_deltas:
                nx, ny = x + dx, y + dy
                neighbor = (nx, ny)
                if (board.is_valid_position(nx, ny) and 
                    not board.is_visited(nx, ny)):
                    total_freedom += degree_cache.get(neighbor, 0)
            
            return (mrv_score, -total_freedom)
        
        return sorted(moves, key=combined_score)
    
    @staticmethod
    def Warnsdorff(moves, knight, board):
        return Heuristics.MRV(moves, knight, board)