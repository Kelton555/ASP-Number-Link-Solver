% define the present numbers as a helper
number(N) :- cell_number(_, N).

% define start/endpoint cells
start_cell(C) :- cell_number(C, _).

% there must be exactly 2 cells of every number on the board
:- #count{C: cell_number(C, N)} != 2, number(N).

% each non-start edge can be assigned exactly 1 number, or no number at all
{edge_number(A, B, N): number(N)} <= 1 :- edge(A, B), not start_cell(A), not start_cell(B), A<B.

% each start cell has exactly one edge number
{edge_number(A, B, N): edge(A, B)} = 1 :- cell_number(A, N).

% reflexive
edge_number(B, A, N) :- edge_number(A, B, N).

% the edges of a cell with a number assigned must be of that number, if they exist
:- cell_number(C, N1), edge_number(C, _, N2), N1!=N2.

% exactly one edge of a cell with a number must be assigned a number
:- cell_number(C, _), #count{C2: edge_number(C, C2, _)} != 1.

% a (non-bridge) cell can only have edge numbers for the same number
%  i.e. only one number can path through a given cell
:- cell(C), edge_number(C, _, N1), not bridge(C), edge_number(C, _, N2), N1!=N2.

% a (non-bridge, non-numbered) cell must have exactly 2 numbered edges
:- cell(C), not start_cell(C), not bridge(C), #count{C2: edge_number(C, C2, _)} != 2. 

% a bridge must have a number assigned to every edge
:- bridge(C1), #sum{1, C2: edge(C1, C2); -1, C2: edge_number(C1, C2, _)} != 0.

% traversable paths through a bridge must share the same number
:- bridge(B), traversable(B, C1, C2), edge_number(B, C1, N1), edge_number(B, C2, N2), N1!=N2.

% each pair of numbered cells must be connected via edges assigned that number
number_path(A, B, N) :- edge_number(A, B, N).
number_path(A, C, N) :- number_path(A, B, N), edge_number(B, C, N).
:- cell_number(C1, N), cell_number(C2, N), C1!=C2, not number_path(C1, C2, N).

% each cell must be able to reach a numbered cell through numbered edges
:- cell(C1), #count{C2: start_cell(C2), number_path(C1, C2, _)} = 0.
