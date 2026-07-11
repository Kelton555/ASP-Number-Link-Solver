<img width="30%" alt="A solved 11x11 number link puzzle with bridges featuring a ring of walls with 4 gaps. Part of the Courtyard Pack from Flow Free: Bridges" src="https://github.com/user-attachments/assets/22a94b39-3fb4-4974-92f4-5fc12fcc0ade" />

<img width="30%" alt="A solved 9x11 number link puzzle with bridges featuring excluded cells. Part of the Hourglass Pack from Flow Free: Bridges" src="https://github.com/user-attachments/assets/d2968858-5276-47d0-a613-727f9a8119e3" />

<img width="30%" alt="A solved 12x12 number link puzzle with bridges featuring pockets of walls around certain cells. Part of the Pockets Pack from Flow Free: Bridges" src="https://github.com/user-attachments/assets/5d777878-fb67-4ff1-9835-89ab5ea35e23" />

# How To Use
View.py is a tkinter-based GUI program to interface with the solver, only working in the very simple rectangle case.

Enter numbers (or the listed letters) into the grid in the GUI as the start/end points of links. You can also enter 'B' or 'b' into a cell to indicate a bridge. You can click in the space between cells to toggle walls, preventing adjacent cells from being connected.

Enter a number of threads to use in solving if you'd like, then click 'Solve' to start the solving process; lines will be drawn indicating a solution when the solving is complete.

The console will log if a situation is unsatisfiable, as well as stats about the solving.

# ASP File Structure
The solver.lp file is where the choice and solving happens. The solver works based on edges rather than cells, meaning that bridges and board shapes are more generalizable. 
(I believe the solver is theoretically capable of solving anything from the Flow series of mobile games: this includes the stranger cases of hexes, shapes, and warps)

The simple_rectangle.lp file is used to translate more human-readable input into predicates used for the solver, making assumptions based specifically on the simple rectangle case.
(Cells are connected by edges by being directly adjacent; bridges always connect above to below and left to right; borders of the board don't wrap; etc.)

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

```wall_xy(X1, Y1, X2, Y2)``` can be used to place a wall between cells (X1, Y1) and (X2, Y2), preventing them from being connected even when they're adjacent

```excluded_xy(X, Y)``` indicates that the cell at (X, Y) in the grid doesn't exist, allowing for interior gaps in a simple rectangle

# Project Policies
Feel free to report any issues you may come across, I'd be glad to take a look and attempt fixes. Also feel free to contribute if you'd like; I may also create translation layers and GUI support for other types of boards at a later date

Note that required dependencies may have different license policies than my code. Everything directly contained in this repository is my own original work and falls under the MIT license; refer to the policies of other projects as necessary.
