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
GRID_START = (100,100)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

LINE_BASE = 5
CELL_SIZE = 50
BOX_BORDER_RATIO = 2
DIGIT_FONT_SIZE = 40
GRID_SIZE = 9

HIGHLIGHT_COOLDOWN = 100

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INPUT_DIGITS = (51, 102, 255)
BLUE = (179, 224, 255)
RED = (200, 0, 25)
GREEN = (25, 255, 64)

FPS = 60

#%% Getting ready for the grid.
class Game:
    def __init__(self,state):
        self.state = state
        self.time = 0

class Frame:    
    def __init__(self, WIN, LINE_BASE,CELL_SIZE, GRID_START, FRAME_COLOR, BOX_BORDER_RATIO, HIGHLIGHT_COLOR,HIGHLIGHT_COOLDOWN):
        self.WIN = WIN
        LINE_FRAME = ([BOX_BORDER_RATIO]+[1]*2)*3 + [BOX_BORDER_RATIO]
        self.LINE_SIZE = [frame * LINE_BASE for frame in LINE_FRAME]
        self.CELL_SIZE = CELL_SIZE
        self.GRID_START = GRID_START
        self.TOTAL_GRID_SIZE = 9*CELL_SIZE + sum(self.LINE_SIZE)
        self.GRID_END = (self.GRID_START[0] + self.TOTAL_GRID_SIZE,
                         self.GRID_START[0] + self.TOTAL_GRID_SIZE)
        
        self.FRAME_COLOR = FRAME_COLOR

        self.lines_create()
        self.corners_create()
        
        self.HIGHLIGHT_COLOR = HIGHLIGHT_COLOR
        self.HIGHLIGHT_COOLDOWN = HIGHLIGHT_COOLDOWN        
        self.active_cell = [-1,-1]
        self.highlight_last_changed = 0
        


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

        self.LINE_STARTS = [line[0] for line in self.LINES[:10]]
            
    def lines_draw(self):
        for line in self.LINES:
            pygame.draw.rect(self.WIN, self.FRAME_COLOR, line)

    def lines_between(self,value):
        for i,line in zip(reversed(range(9)),reversed(self.LINE_STARTS[:-1])):
            if value > line:
                return i

    def corners_create(self):
        LINEAR_CORNERS = [start + thickness for start,thickness in zip(self.LINE_STARTS,self.LINE_SIZE)]
        
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
        self.DIGIT_FONT_SIZE = DIGIT_FONT_SIZE
        
        self.CELL_SIZE = CELL_SIZE
        
        self.SIZE = GRID_SIZE
        self.grid = np.zeros((self.SIZE,self.SIZE),dtype = int)
        self.givens = np.zeros((self.SIZE,self.SIZE),dtype = int)
        
        self.INPUT_COLOR = INPUT_COLOR
        self.GIVEN_COLOR = GIVEN_COLOR
        
        self.solve_show = False
                    
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
    
    def digits_draw(self, tick):
        # Checks whether the grid is complete.
        self.INPUT_COLOR = INPUT_DIGITS
        if self.digits_check_all():
            self.INPUT_COLOR = GREEN
        
        # Filling in numbers.    
        for i in range(9):
            for j in range(9):
                if self.grid[i,j] != 0:
                    if not self.givens[i,j]:
                        if self.cell_check_n_placed(i,j,self.grid[i,j]):
                            cell_text = CenteredText(str(self.grid[i,j]), self.DIGIT_FONT_SIZE,
                                                     self.FRAME.CELL_CORNERS[i,j][0],
                                                     self.FRAME.CELL_CORNERS[i,j][1],
                                                     self.CELL_SIZE, self.CELL_SIZE,
                                                     self.INPUT_COLOR)   
                        else:
                            cell_text = CenteredText(str(self.grid[i,j]), self.DIGIT_FONT_SIZE,
                                                     self.FRAME.CELL_CORNERS[i,j][0],
                                                     self.FRAME.CELL_CORNERS[i,j][1],
                                                     self.CELL_SIZE, self.CELL_SIZE,
                                                     RED)                               
                    else:
                        cell_text = CenteredText(str(self.grid[i,j]), self.DIGIT_FONT_SIZE,
                                                 self.FRAME.CELL_CORNERS[i,j][0],
                                                 self.FRAME.CELL_CORNERS[i,j][1],
                                                 self.CELL_SIZE, self.CELL_SIZE,
                                                 self.GIVEN_COLOR)
                    cell_text.draw(self.WIN)
                    
        # If backtracking is active, draw in the digits one at a time.
        if self.solve_show and len(self.backtracking_solution_path) > 0:
            self.solve_show_counter  += tick
            if self.solve_show_counter > self.solve_show_counter_required:
                self.solve_show_counter -= self.solve_show_counter_required
                x, y, n = self.backtracking_solution_path.pop(0)
                self.grid[x, y] = n

        
    def digits_check_all(self):
        correct = False
        if self.grid.sum() == 405:
            correct = True
            for i in range(9):
                for j in range(9):
                    if not self.givens[i,j]:
                        if not self.cell_check_n_placed(i,j,self.grid[i,j]):
                            correct = False
        return correct
            
               
            
        
        
    # Function to get the box a row, column cell belongs to.        
    def cell_get_box(self, r, c):
        return self.grid[(r//3)*3:(r//3+1)*3,(c//3)*3:(c//3+1)*3]


    # Checks if the digit n can be in cell r,c, where r is row and c is column.
    def cell_check_n(self, r, c, n, debug=False):
        if n in self.grid[r,:]:
            if debug:
                print(f'{n} in row')
            return False
        elif n in self.grid[:,c]:
            if debug:
                print(f'{n} in column')
            return False
        elif n in self.cell_get_box(r, c):
            if debug:
                print(f'{n} in box')
            return False
        else:
            return True

    # Checks whether the digit n in position r,c can see any *other* digit n.
    def cell_check_n_placed(self,r,c,n):
        self.grid[r, c] = 0
        check = self.cell_check_n(r, c, n)
        self.grid[r, c] = n
        return check
    
    def solve_backtracking(self):
        self.backtracking_path = []
        self.solve_backtracking_algorithm(self.grid)
        self.solve_backtracking_get_path()
        self.solve_show = True
        self.solve_show_counter = 0    
        self.solve_show_counter_required = 200
    
    def solve_backtracking_algorithm(self, grid):
        for r in range(9): # Row
            for c in range(9): # Column
                if self.grid[r,c] == 0:
                    for n in range(1,10):
                        if self.cell_check_n(r, c, n):
                            self.backtracking_path.append((r, c, n))
                            self.grid[r,c] = n
                            self.solve_backtracking_algorithm(self.grid)
                            self.backtracking_path.append((r, c, 0))
                            self.grid[r,c] = 0
                    return
        self.backtracking_path.append(np.copy(self.grid))

    def solve_backtracking_get_path(self):
        self.solutions = []
        solution_int = int
        for i,val in enumerate(self.backtracking_path):
            if len(val) > 3:
                self.solutions.append(val)
                solution_int = i
                
        if len(self.solutions) == 1:
            self.backtracking_solution_path = [val for i,val in enumerate(self.backtracking_path) if i < solution_int]
        else:
            raise ValueError('Either no or multiple solutions!')

# Class shamelessly stolen from the internet.
class CenteredText(object):
    """ Centered Text Class
    """
    def __init__(self, text, text_size, x, y, w, h, color = (0, 0, 0)):
        self.x, self.y, self.w, self.h = x,y,w,h
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", text_size)
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
def start_draw_window():
    WIN.fill((WHITE))

    CenteredText('Peter\'s Sudoku!',80,50,100,620,100,BLACK).draw(WIN)

    CenteredText('Play',60,300,250,120,100,BLACK).draw(WIN)

    
    pygame.display.update()
    
def start_handle_input(event,game):
    if event.type == pygame.MOUSEBUTTONDOWN:
        coor = pygame.mouse.get_pos()
        if 300 <= coor[0] <= 420 and 250 <= coor[1] <= 350:
            game.state = 'play'
       
   

def sudoku_draw_window(active_cell, frame, grid, tick):
    WIN.fill((WHITE))
    
    frame.highlight_cells()

    frame.lines_draw()
        
    grid.digits_draw(tick)
        
    pygame.display.update()

def sudoku_handle_input(event, game, frame, grid):
    if event.type == pygame.MOUSEBUTTONDOWN:
        coor = pygame.mouse.get_pos()
        if frame.GRID_START[0] <= coor[0] <= frame.GRID_END[0] and frame.GRID_START[1] <= coor[1] <= frame.GRID_END[1]:
            cell_x = frame.lines_between(coor[0])
            cell_y = frame.lines_between(coor[1])     
            if frame.active_cell == [cell_x,cell_y]:
                if frame.highlight_last_changed + frame.HIGHLIGHT_COOLDOWN < game.time:
                    frame.active_cell = [-1,-1]
            else:
                frame.active_cell = [cell_x, cell_y]
                frame.highlight_last_changed = game.time 
                
    if event.type == pygame.KEYDOWN:
        if frame.active_cell != [-1,-1]:
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
            
            
            if event.key == pygame.K_UP:
                if frame.active_cell[1] > 0:
                    frame.active_cell[1] -= 1
            if event.key == pygame.K_DOWN:
                if frame.active_cell[1] < 8:
                    frame.active_cell[1] += 1
            if event.key == pygame.K_LEFT:
                if frame.active_cell[0] > 0:
                    frame.active_cell[0] -= 1
            if event.key == pygame.K_RIGHT:
                if frame.active_cell[0] < 8:
                    frame.active_cell[0] += 1
                
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            grid.solve_backtracking()
                

def main():
    clock = pygame.time.Clock()
    run = True
    active_cell = [-1,-1]
    
    game = Game('start')
    frame = Frame(WIN, LINE_BASE, CELL_SIZE, GRID_START, BLACK, BOX_BORDER_RATIO, BLUE, HIGHLIGHT_COOLDOWN)
    grid = Grid(WIN, frame, 'comicsans', DIGIT_FONT_SIZE, CELL_SIZE, GRID_SIZE, INPUT_DIGITS, BLACK)

    grid.load_from_file(grid_name)
                
    while run:
        clock.tick(FPS)
        game.time += clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if game.state == 'start':
                start_handle_input(event,game)
            elif game.state == 'play':
                sudoku_handle_input(event, game, frame, grid)
                
        
        if game.state == 'start':            
            start_draw_window()
                
        elif game.state == 'play':
            sudoku_draw_window(active_cell, frame, grid, clock.tick(FPS))
    
    pygame.quit()
    

if __name__ == '__main__':
    main()