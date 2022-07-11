# Sudoku application
Goal: Create a small application where an user can play Sudoku, as well as see it being solved via brute-force (recursion where things are tried until a solution is reached) or attempted via pre-programmed analytical methods.

Already implemented:
* Brute-force solver via recursion.
* Creating a GUI via Pygame where the player can try to solve the Sudoku on their own.

Next stage:
* Animating the brute-force solution, letting the player see what's happening one step at a time.
* Make sure the program knows the finished grid, as to be able to compare to that. (?)
* Clean up code a bit, move things into classes.
* Highlight errors as can be seen with the current grid.

Future features:
* Create a starting screen.
* Let the player load from different Sudoku. Possibly also upload their own?
* Programming an analytical solver, starting with the following Sudoku techniques: naked singles, hidden singles, hidden pairs/triples/quadruples, and X-wings.
* Rating Sudokus with the analytical solver, based on how many and which techniques it had to use.