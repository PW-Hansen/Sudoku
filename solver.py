import numpy as np

#%% Setting up the board.
# Sudoku found online and copy-pasted. 0s denote empty grid positions.
grid = np.array(  [[0, 0, 0, 1, 0, 0, 4, 0, 0],
                   [0, 0, 4, 0, 9, 0, 0, 6, 2],
                   [0, 0, 0, 7, 0, 0, 0, 3, 0],
                   [5, 0, 0, 0, 0, 0, 0, 1, 0],
                   [1, 0, 0, 6, 8, 3, 0, 0, 0],
                   [3, 4, 0, 0, 1, 0, 0, 0, 0],
                   [0, 0, 6, 0, 7, 0, 0, 4, 5],
                   [8, 0, 1, 3, 4, 0, 0, 0, 6],
                   [0, 0, 0, 0, 0, 6, 0, 0, 1]])

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
    
    
def cell_options_get(grid):
    grid_options = np.zeros((9,9), dtype = list)
    for r in range(9):
        for c in range(9):
            if grid[r,c] == 0:
                options = []
                for n in range(1,10):
                    if cell_check_n(grid,r,c,n):
                        options.append(n)
                grid_options[r,c] = options
                
    return grid_options

# Removes a placed digit as possibility from all cells it can see.
def cell_options_remove(grid_options, r, c, n):
    for cell in grid_options[:,c]:
        if cell != 0:
            if n in cell:
                cell.remove(n)
                
    for cell in grid_options[r,:]:
        if cell != 0:
            if n in cell:
                cell.remove(n)
    
    for i in range(3):
        for j in range(3):
            cell_opt_vals = grid_options[3*(r // 3) + i, 3*(c // 3) + j]
            if cell_opt_vals != 0:
                if n in cell_opt_vals:
                    cell_opt_vals.remove(n)
    
    return grid_options

def find_hidden_singles(cells):
    return_dict = {}
    numbers = []
    for cell in cells:
        if cell != 0:
            numbers += cell

    numbers_dict = {}    
    for cell in numbers:
        if cell in numbers_dict: 
            numbers_dict[cell] += 1
        else: 
            numbers_dict[cell] = 1

    for i,val in enumerate(cells):
        if val != 0:
            for n in val:
                if numbers_dict[n] == 1:
                    return_dict[i] = n
    
    return return_dict

def find_pointing_pairs(cells):
    pairs_dict = {}
    for i,cell1 in enumerate(cells):
        for j,cell2 in enumerate(cells):
            if cell1 != 0:
                if i != j and cell1 == cell2 and len(cell1) == 2:
                    key = [i,j]
                    key.sort()
                    pairs_dict[tuple(key)] = cell1
                    
    return pairs_dict

def execute_pointing_pairs_dict(cells, pairs_dict):
    for pair_pos,pair_vals in pairs_dict.items():
        for i,cell in enumerate(cells):
            if cell != 0 and i not in pair_pos:
                for n in pair_vals:
                    if n in cell:
                        cell.remove(n)
    return cells

def cell_place_digit(grid, grid_options, r, c, n):
    grid[r, c] = n
    grid_options[r, c] = 0
    grid_options = cell_options_remove(grid_options, r, c, n)
    
    return grid, grid_options

def analytical_solve_naked_single(grid, grid_options):
    run = True
    while run:
        run = False
        for r in range(9):
            for c in range(9):
                if grid_options[r, c] != 0:
                    if len(grid_options[r, c]) == 1:
                        n = grid_options[r, c][0]
                        grid, grid_options = cell_place_digit(grid, grid_options, r, c, n)
                        run = True
    
def analytical_solve_hidden_single(grid, grid_options):
    run = True
    while run:
        run = False
        for r in range(9):
            hidden_singles_dict = find_hidden_singles(grid_options[r,:])
            for c,n in hidden_singles_dict.items():
                grid, grid_options = cell_place_digit(grid, grid_options, r, c, n)
                run = True
        for c in range(9):
            hidden_singles_dict = find_hidden_singles(grid_options[:,c])
            for r,n in hidden_singles_dict.items():
                grid, grid_options = cell_place_digit(grid, grid_options, r, c, n)
                run = True
            
        for i in range(3):
            for j in range(3):
                box_options = grid_options[i*3:i*3+3, j*3:j*3+3]
                hidden_singles_dict = find_hidden_singles(np.reshape(box_options,(1,9))[0])
                for k,n in hidden_singles_dict.items():
                    r = i*3 + k // 3
                    c = j*3 + k % 3
                    
                    grid, grid_options = cell_place_digit(grid, grid_options, r, c, n)
                    run = True
    
def analytical_solve_pointing_pair(grid_options):
    run = True
    while run: 
        run = False
        for r in range(9):
            pairs_dict = find_pointing_pairs(grid_options[r,:])
            execute_pointing_pairs_dict(grid_options[r,:], pairs_dict)
       
        for c in range(9):
            pairs_dict = find_pointing_pairs(grid_options[:,c])
            execute_pointing_pairs_dict(grid_options[:,c], pairs_dict)
        for i in range(3):
            for j in range(3):
                box_options = grid_options[i*3:i*3+3, j*3:j*3+3]
                reshaped_cells = np.reshape(box_options,(1,9))[0]
                pairs_dict = find_pointing_pairs(reshaped_cells)
                reshaped_cells = execute_pointing_pairs_dict(reshaped_cells, pairs_dict)
                grid_options[i*3:i*3+3, j*3:j*3+3]
                  
grid_options = cell_options_get(grid)
for i in range(10):
    analytical_solve_naked_single(grid, grid_options)
    analytical_solve_hidden_single(grid, grid_options)
    analytical_solve_pointing_pair(grid_options)
