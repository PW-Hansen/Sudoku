import numpy as np

#%% Setting up the board.
# Sudoku found online and copy-pasted. 0s denote empty grid positions.
grid = np.matrix([[2,8,0,5,0,0,4,9,1],
                 [0,0,1,0,3,0,0,0,5],
                 [0,0,0,1,0,9,6,0,8],
                 [0,1,6,7,8,5,9,0,0],
                 [4,7,0,3,9,2,5,1,6],
                 [9,0,0,0,1,0,0,8,0],
                 [0,0,7,9,4,3,0,5,2],
                 [8,2,0,6,5,1,0,0,3],
                 [5,3,4,0,7,0,0,6,0]])

# Function to get the box a row, column cell belongs to.
def cell_get_box(grid, r, c):
    return grid[(r//3)*3:(r//3+1)*3,(c//3)*3:(c//3+1)*3]

# Checks if the digit n can be in cell r,c, where r is row and c is column.
def cell_check_n(grid, r, c, n, debug=False):
    if n in grid[r,:]:
        if debug:
            print(f'{n} in row')
        return False
    elif n in grid[:,c]:
        if debug:
            print(f'{n} in column')
        return False
    elif n in cell_get_box(grid, r, c):
        if debug:
            print(f'{n} in box')
        return False
    else:
        return True

# Analytical help_functions.
def cell_check_options(grid, r, c):
    cell_seen = np.concatenate((
                    np.asarray(grid[r,:]).flatten(),\
                    np.asarray(grid[:,c]).flatten(),\
                    np.asarray(cell_get_box(grid, r, c)).flatten()
                ))
    
    cell_options = [n for n in range(1,10) if n not in cell_seen]    
    
    return cell_options


def solve_brute_force(grid):
    for r in range(9): # Row
        for c in range(9): # Column
            if grid[r,c] == 0:
                for n in range(1,10):
                    if cell_check_n(grid, r, c, n):
                        grid[r,c] = n
                        solve_brute_force(grid)
                        grid[r,c] = 0
                return    
    print(grid)
