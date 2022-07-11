#%% Sudoku project
# Goals:
# * Create a brute-force solver using recursion.
# * Create a GUI which can be used to play Sudoku.
# Compare the finished grid to the brute-force solution.
# Move things into classes.
# See recursion in action.
# Create a solver which will attempt to use analytical methods to solve the
# Sudoku.
# Rating system for the Sudoku via the analytical solver.
# Sudoku generator after setting a desired difficulty.

#%%
import pygame
import numpy as np
pygame.font.init()


grid_name = 'grid_1.csv'

WIDTH, HEIGHT = 720, 720

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INPUT_DIGITS = (51, 102, 255)
BLUE = (179, 224, 255)

FPS = 60

#%% Getting ready for the grid.
LINE_THICKNESS = [10, 5, 5, 10, 5, 5, 10, 5, 5, 10]
CELL_THICKNESS = 50

TOTAL_GRID_SIZE = 9*CELL_THICKNESS + sum(LINE_THICKNESS)

GRID_START = (100, 100)


# Lines for the grid.
LINES = []

# First vertical lines.
for i,line in enumerate(LINE_THICKNESS):
    x,y = GRID_START
    x+= CELL_THICKNESS*i + sum(LINE_THICKNESS[:i])
    
    LINES.append(pygame.Rect(x,y,LINE_THICKNESS[i],TOTAL_GRID_SIZE))
    
# Then horizontal lines.
for i,line in enumerate(LINE_THICKNESS):
    x,y = GRID_START
    y+= CELL_THICKNESS*i + sum(LINE_THICKNESS[:i])
    
    LINES.append(pygame.Rect(x,y,TOTAL_GRID_SIZE,LINE_THICKNESS[i]))

# Grabbing line starts
LINE_STARTS = [line[0] for line in LINES[:10]]

# Gets the highest line in LINE_STARTS which the value is lower than.
def between_lines(value):
    for i,line in zip(reversed(range(10)),reversed(LINE_STARTS)):
        if value > line:
            return i


#%% Preparing text.
DIGIT_FONT_SIZE = 40
DIGIT_FONT = pygame.font.SysFont('comicsans', DIGIT_FONT_SIZE)
DIGIT_TEXT = ['']*9

for i in range(9):
    DIGIT_TEXT[i] = DIGIT_FONT.render(str(i+1), 1, BLACK)
    
# Cell corners.
LINEAR_CORNERS = [start + thickness for start,thickness in zip(LINE_STARTS,LINE_THICKNESS)]

CELL_CORNERS = np.empty((9,9),dtype = tuple)
for i in range(9):
    for j in range(9):
        CELL_CORNERS[i,j] = (LINEAR_CORNERS[i], 
                             LINEAR_CORNERS[j])

# Class shamelessly stolen from the internet.
class CenteredText(object):
    """ Centered Text Class
    """
    def __init__(self, text, x, y, w, h, color = (0, 0, 0)):
        self.x, self.y, self.w, self.h = x,y,w,h
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", 40)
        width, height = font.size(text)
        xoffset = (self.w-width) // 2
        yoffset = (self.h-height) // 2
        self.coords = self.x+xoffset, self.y+yoffset
        self.txt = font.render(text, True, color)

    def draw(self, screen):
        screen.blit(self.txt, self.coords)
        # for testing purposes, draw the rectangle too
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(screen, (0,0,0), rect, 1)


#%%
# Function to return which cell of the Sudoku is clicked in the format row, column.
def get_cell_click(coordinates):
    grid_start  = GRID_START[0] + LINE_THICKNESS[0]
    grid_end    = GRID_START[0] + TOTAL_GRID_SIZE
    if grid_start <= coordinates[0] <= grid_end and grid_start <= coordinates[1] <= grid_end:
        row = between_lines(coordinates[0])
        col = between_lines(coordinates[1])
    
    return row,col

def draw_window(active_cell,grid,GRID_INPUT):
    WIN.fill((WHITE))
    
    # Highlighting active cell.
    if active_cell != [-1,-1]:
        cell_x, cell_y = active_cell
        cell = pygame.Rect(LINE_STARTS[cell_x]+LINE_THICKNESS[cell_x],
                           LINE_STARTS[cell_y]+LINE_THICKNESS[cell_y],
                           CELL_THICKNESS, CELL_THICKNESS)
        pygame.draw.rect(WIN, BLUE, cell)
        

    # Drawing Sudoku grid.
    for line in LINES:
        pygame.draw.rect(WIN, BLACK, line)
    
    # Filling in numbers.    
    for i in range(9):
        for j in range(9):
            if grid[i,j] != 0:
                if GRID_INPUT[i,j]:
                    cell_text = CenteredText(str(grid[i,j]),
                                             CELL_CORNERS[i,j][0],CELL_CORNERS[i,j][1],
                                             CELL_THICKNESS,CELL_THICKNESS,
                                             INPUT_DIGITS)                
                else:
                    cell_text = CenteredText(str(grid[i,j]),
                                             CELL_CORNERS[i,j][0],CELL_CORNERS[i,j][1],
                                             CELL_THICKNESS,CELL_THICKNESS,
                                             BLACK)
                cell_text.draw(WIN)
        
    pygame.display.update()

def handle_input_sudoku(event, active_cell, grid, GRID_INPUT):
    if event.type == pygame.MOUSEBUTTONDOWN:
        cell_x,cell_y = get_cell_click(pygame.mouse.get_pos())
        if (active_cell[0],active_cell[1]) == (cell_x,cell_y):
            active_cell = [-1,-1]
        else:
            active_cell = [cell_x, cell_y]
    if active_cell != [-1,-1] and event.type == pygame.KEYDOWN:
        x,y = active_cell
        if event.key == pygame.K_1 or event.key == pygame.K_KP1:
            if GRID_INPUT[x,y]:
                grid[x,y] = 1
        if event.key == pygame.K_2 or event.key == pygame.K_KP2:
            if GRID_INPUT[x,y]:
                grid[x,y] = 2
        if event.key == pygame.K_3 or event.key == pygame.K_KP3:
            if GRID_INPUT[x,y]:
                grid[x,y] = 3
        if event.key == pygame.K_4 or event.key == pygame.K_KP4:
            if GRID_INPUT[x,y]:
                grid[x,y] = 4
        if event.key == pygame.K_5 or event.key == pygame.K_KP5:
            if GRID_INPUT[x,y]:
                grid[x,y] = 5
        if event.key == pygame.K_6 or event.key == pygame.K_KP6:
            if GRID_INPUT[x,y]:
                grid[x,y] = 6
        if event.key == pygame.K_7 or event.key == pygame.K_KP7:
            if GRID_INPUT[x,y]:
                grid[x,y] = 7
        if event.key == pygame.K_8 or event.key == pygame.K_KP8:
            if GRID_INPUT[x,y]:
                grid[x,y] = 8
        if event.key == pygame.K_9 or event.key == pygame.K_KP9:
            if GRID_INPUT[x,y]:
                grid[x,y] = 9
        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
            if GRID_INPUT[x,y]:
                grid[x,y] = 0
    
    return active_cell, grid
    

def load_grid(grid_name):
    return np.genfromtxt(grid_name, dtype = int, delimiter = ',')


def main():
    clock = pygame.time.Clock()
    run = True
    active_cell = [-1,-1]
    
    grid = load_grid(grid_name)
    GRID_INPUT = np.ones((9,9))
    for i in range(9):
        for j in range(9):
            if grid[i,j] != 0:
                GRID_INPUT[i,j] = 0
    
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            active_cell, grid = handle_input_sudoku(event, active_cell, grid, GRID_INPUT)
                
        draw_window(active_cell,grid,GRID_INPUT)
    
    pygame.quit()
    

if __name__ == '__main__':
    main()