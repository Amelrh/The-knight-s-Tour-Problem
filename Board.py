class Board:
    
    def __init__(self, size=8):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.visited = set()
    
    def is_valid_position(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size
    
    def is_visited(self, x, y):
        return (x, y) in self.visited
    
    def mark_visited(self, x, y, move_number):
        self.grid[x][y] = move_number
        self.visited.add((x, y))
    
    def unmark_visited(self, x, y):
        self.grid[x][y] = None
        self.visited.remove((x, y))
    
    @property
    def path(self):
        path = []
        for move_number in range(self.size * self.size):
            for i in range(self.size):
                for j in range(self.size):
                    if self.grid[i][j] == move_number:
                        path.append((i, j))
                        break
        return path
    
    def display(self):
        print("\nPlateau du Knight's Tour:")
        print("=" * 40)
        for row in self.grid:
            for cell in row:
                if cell is not None:
                    print(f"{cell:2d}", end=" ")
                else:
                    print(" .", end=" ")
            print()
        print("=" * 40)
