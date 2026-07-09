# How To Use
View.py is a tkinter-based GUI program to interface with the solver, only working in the very simple rectangle case (no interior walls, no disconnects, etc.).

Enter numbers into the grid in the GUI as the start/end points of links. You can also enter 'B' or 'b' into a cell to indicate a bridge.
Click 'Solve' to start the solving process; lines will be drawn indicating a solution when the solving is complete.

The console will log if a situation is unsatisfiable, as well as stats about the solving.

# ASP File Structure
The solver.lp file is where the choice and solving happens. The solver works based on edges rather than cells, meaning that bridges and board shapes are more generalizable. 
(I believe the solver is theoretically capable of solving anything from the Flow series of mobile games: this includes the stranger cases of hexes, shapes, and warps)

The simple_rectangle.lp file is used to translate more human-readable input into predicates used for the solver, making assumptions based specifically on the simple rectangle case.
(Cells are connected by edges by being directly adjacent in all cases; bridges always connect above to below and left to right; borders of the board don't wrap; etc.)

# ASP Solver Predicate Structure
```cell(C)``` indicates the ID of a valid cell

```edge(A, B)``` indicates that cell A and cell B are connected (all edges are bi-directional)

```cell_number(C, N)``` indicates that cell C is a start/endpoint for number N

```bridge(C)``` indicates that cell C is a bridge (cannot be a start/endpoint)

```traversable(B, C1, C2)``` indicates that C1 can traverse to C2 via bridge B (and vice-versa)

```edge_number(A, B, N)``` indicates that the edge between cell A and cell B is used for the linking the number N

# Fact Structure for Simple Rectangle Translator
```board_type(simple_rectangle).``` must be declared as a fact to utilize the simple rectangle translation file

```x_size(X)``` and ```y_size(Y)``` are used to indicate the X and Y dimensions of the board. 
  By convention, X=Y=1 is the top left cell on the board

```num_at(N, X, Y)``` can be used to place a number start/endpoint at position (X, Y) (X=Y=1 is the top left corner)

```bridge_xy(X, Y)``` can be used to place a bridge at a given (X, Y) position (X=Y=1 is the top left corner)
