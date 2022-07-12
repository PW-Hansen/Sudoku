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
class Frame:    
    def __init__(self, WIN, LINE_BASE,CELL_SIZE, GRID_START, FRAME_COLOR, BOX_BORDER_RATIO, HIGHLIGHT_COLOR):
        self.WIN = WIN
        LINE_FRAME = ([BOX_BORDER_RATIO]+[1]*2)*3 + [BOX_BORDER_RATIO]
        self.LINE_SIZE = [frame * LINE_BASE for frame in LINE_FRAME]
        self.CELL_SIZE = CELL_SIZE
        self.GRID_START = GRID_START
        self.TOTAL_GRID_SIZE = 9*CELL_SIZE + sum(LINE_SIZE)
        self.GRID_END = (self.GRID_START[0] + self.TOTAL_GRID_SIZE,
                         self.GRID_START[0] + self.TOTAL_GRID_SIZE)
        
        self.FRAME_COLOR = FRAME_COLOR

        self.lines_create()
        
        self.corners_create()
        
        self.HIGHLIGHT_COLOR = HIGHLIGHT_COLOR
        self.active_cell = [-1,-1]
        

    def lines_create(self):
        self.LINES = []
        
        # First vertical lines.
        for i,line in enumerate(self.LINE_SIZE):
            x,y = self.GRID_START
            x += self.CELL_SIZE*i + sum(self.LINE_SIZE[:i])
            
            self.LINES.append(pygame.Rect(x,y,self.LINE_SIZE[i],self.TOTAL_GRID_SIZE))
            
        # Then horizontal lines.
        for i,line in enumerate(self.LINE_SIZE):
            x,y = self.GRID_START
            y += self.CELL_SIZE*i + sum(self.LINE_SIZE[:i])
            
            self.LINES.append(pygame.Rect(x,y,self.TOTAL_GRID_SIZE,self.LINE_SIZE[i]))
            
    def lines_draw(self):
        for line in self.LINES:
            pygame.draw.rect(self.WIN, self.FRAME_COLOR, line)

    def corners_create(self):
        LINE_STARTS = [line[0] for line in self.LINES[:10]]
        LINEAR_CORNERS = [start + thickness for start,thickness in zip(LINE_STARTS,self.LINE_SIZE)]
        
        self.CELL_CORNERS = np.empty((9,9),dtype = tuple)
        for i in range(9):
            for j in range(9):
                self.CELL_CORNERS[i,j] = (LINEAR_CORNERS[i], 
                                          LINEAR_CORNERS[j])

    def highlight_cells(self):
        if self.active_cell != [-1,-1]:
            cell_start_x, cell_start_y = self.CELL_CORNERS[tuple(self.active_cell)]
            cell = pygame.Rect(cell_start_x,cell_start_y,
                               self.CELL_SIZE, self.CELL_SIZE)
            pygame.draw.rect(self.WIN, self.HIGHLIGHT_COLOR, cell)
            


class Grid:
    def __init__(self, WIN, FRAME, DIGIT_FONT_NAME, DIGIT_FONT_SIZE, CELL_SIZE, GRID_SIZE, INPUT_COLOR, GIVEN_COLOR):
        self.WIN = WIN
        self.FRAME = FRAME
        
        FRAME.GRID = self
        
        self.DIGIT_FONT = pygame.font.SysFont(DIGIT_FONT_NAME, DIGIT_FONT_SIZE)
        
        self.CELL_SIZE = CELL_SIZE
        
        self.SIZE = GRID_SIZE
        self.grid = np.zeros((self.SIZE,self.SIZE),dtype = int)
        self.givens = np.zeros((self.SIZE,self.SIZE),dtype = int)
        
        self.INPUT_COLOR = INPUT_COLOR
        self.GIVEN_COLOR = GIVEN_COLOR
            
    def load_from_file(self, grid_name):
        self.grid = np.genfromtxt(grid_name, dtype = int, delimiter = ',')
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.grid[i,j] != 0:
                    self.givens[i,j] = 1
        
    def digits_change(self, i, j, n):
        if type(n) != int:
            raise ValueError('Tried to put a non-int number into the grid.')
        elif n < 0 or n > self.SIZE:
            raise ValueError('Tried to put a too large number into the grid!')
        else:
            self.grid[i,j] = n
    
    def digits_draw(self):
        # Filling in numbers.    
        for i in range(9):
            for j in range(9):
                if self.grid[i,j] != 0:
                    if not self.givens[i,j]:
                        cell_text = CenteredText(str(self.grid[i,j]),
                                                 self.FRAME.CELL_CORNERS[i,j][0],
                                                 self.FRAME.CELL_CORNERS[i,j][1],
                                                 self.CELL_SIZE,self.CELL_SIZE,
                                                 self.INPUT_COLOR)                
                    else:
                        cell_text = CenteredText(str(self.grid[i,j]),
                                                 self.FRAME.CELL_CORNERS[i,j][0],
                                                 self.FRAME.CELL_CORNERS[i,j][1],
                                                 self.CELL_SIZE,self.CELL_SIZE,
                                                 self.GIVEN_COLOR)
                    cell_text.draw(self.WIN)
        
        

#%%
LINE_SIZE = [10, 5, 5, 10, 5, 5, 10, 5, 5, 10]
CELL_SIZE = 50

TOTAL_GRID_SIZE = 9*CELL_SIZE + sum(LINE_SIZE)

GRID_START = (100, 100)


# Lines for the grid.
LINES = []

# First vertical lines.
for i,line in enumerate(LINE_SIZE):
    x,y = GRID_START
    x+= CELL_SIZE*i + sum(LINE_SIZE[:i])
    
    LINES.append(pygame.Rect(x,y,LINE_SIZE[i],TOTAL_GRID_SIZE))
    
# Then horizontal lines.
for i,line in enumerate(LINE_SIZE):
    x,y = GRID_START
    y+= CELL_SIZE*i + sum(LINE_SIZE[:i])
    
    LINES.append(pygame.Rect(x,y,TOTAL_GRID_SIZE,LINE_SIZE[i]))

# Grabbing line starts
LINE_STARTS = [line[0] for line in LINES[:10]]

# Gets the highest line in LINE_STARTS which the value is lower than.
def between_lines(value):
    for i,line in zip(reversed(range(10)),reversed(LINE_STARTS)):
        if value > line:
            return i


#%% Preparing text.
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
    grid_start  = GRID_START[0] + LINE_SIZE[0]
    grid_end    = GRID_START[0] + TOTAL_GRID_SIZE

    if grid_start <= coordinates[0] <= grid_end and grid_start <= coordinates[1] <= grid_end:
        row = between_lines(coordinates[0])
        col = between_lines(coordinates[1])
        return row,col
    
    else:
        return False,False

def draw_window(active_cell,frame,grid):
    WIN.fill((WHITE))
    
    frame.highlight_cells()

    frame.lines_draw()
    
    grid.digits_draw()
        
    pygame.display.update()

def handle_input_sudoku(event, frame, grid):
    if event.type == pygame.MOUSEBUTTONDOWN:
        coor = pygame.mouse.get_pos()
        if frame.GRID_START[0] <= coor[0] <= frame.GRID_END[0] and frame.GRID_START[1] <= coor[1] <= frame.GRID_END[1]:
            cell_x = between_lines(coor[0])
            cell_y = between_lines(coor[1])     
            if frame.active_cell == [cell_x,cell_y]:
                frame.active_cell = [-1,-1]
            else:
                frame.active_cell = [cell_x, cell_y]
                
    if frame.active_cell != [-1,-1] and event.type == pygame.KEYDOWN:
        x,y = frame.active_cell
        if not grid.givens[x,y]:
            if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                grid.grid[x,y] = 1
            if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                grid.grid[x,y] = 2
            if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                grid.grid[x,y] = 3
            if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                grid.grid[x,y] = 4
            if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                grid.grid[x,y] = 5
            if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                grid.grid[x,y] = 6
            if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                grid.grid[x,y] = 7
            if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                grid.grid[x,y] = 8
            if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                grid.grid[x,y] = 9
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                grid.grid[x,y] = 0    

def main():
    clock = pygame.time.Clock()
    run = True
    active_cell = [-1,-1]
    
    frame = Frame(WIN, 5, 50, (100,100), BLACK, 2, BLUE)
    grid = Grid(WIN, frame, 'comicsans', 40, 50, 9, INPUT_DIGITS, BLACK)
    
    grid.load_from_file(grid_name)
    
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            handle_input_sudoku(event, frame, grid)
                
        draw_window(active_cell,frame,grid)
    
    pygame.quit()
    

if __name__ == '__main__':
    main()