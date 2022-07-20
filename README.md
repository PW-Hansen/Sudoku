# Sudoku application
Goal: Create a small application where an user can play Sudoku, as well as see it being solved via brute-force (recursion where things are tried until a solution is reached) or attempted via pre-programmed analytical methods.

Already implemented:
* Brute-force solver via recursion.
* Creating a GUI via Pygame where the player can try to solve the Sudoku on their own.
* Highlight errors as can be seen with the current grid.
* Clean up code a bit, move things into classes.
* App now checks if the grid is complete (and correct), and if so, changes input digit color to green.
* Allow navigation of highlighted cell via arrowkeys.
* Animating the brute-force solution, letting the player see what's happening one step at a time.
* Create a starting screen.
* Add timer.
* Let the player load different Sudoku.
* Analytical solver progress: naked singles, hidden singles, pointing pairs.

Next stage:
* Programming an analytical solver, starting with the following Sudoku techniques: hidden pairs/triples/quadruples?, and X-wings (?).

Future features:
* Rating Sudokus with the analytical solver, based on how many and which techniques it had to use.
* More code cleanup.
* Let player create Sudoku?

Potential stretch
* Pencilmarks, both corner and center?
* Multiple cell selection.
* Highlight seen cells?