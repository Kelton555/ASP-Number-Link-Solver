% contents of this file are only run if the board type is
%  'simple_rectangle'

% calculate amount of tiles
tile_count(Z) :- Z=X*Y, x_size(X), y_size(Y), board_type(simple_rectangle).

% define cells
cell(1..Y) :- tile_count(Y), board_type(simple_rectangle).

% convert XY bridge coordinate to bridge predicate
bridge(C) :- cell(C), x_size(XS), bridge_xy(X, Y), C=X+((Y-1)*XS), board_type(simple_rectangle).

% convert XY wall coordinates to wall predicate
wall(C1, C2) :- wall_xy(X1, Y1, X2, Y2), cell(C1), cell(C2), x_size(XS), C1=X1+((Y1-1)*XS), C2=X2+((Y2-1)*XS), board_type(simple_rectangle).
% walls are reflexive
wall(C2, C1) :- wall(C1, C2).

% define edges based on rectangle layout (accounting for in-board walls)
% horizontal connections
edge(C1, C2) :- cell(C1), cell(C2), C2-C1=1, (C2-1)\X_SIZE != 0, x_size(X_SIZE), not wall(C1, C2), board_type(simple_rectangle).
% vertical connections
edge(C1, C2) :- cell(C1), cell(C2), C2-C1=X_SIZE, x_size(X_SIZE), not wall(C1, C2), board_type(simple_rectangle).
% reflexivity
edge(C2, C1) :- edge(C1, C2), board_type(simple_rectangle).

% bridges use a traversable predicate to indicate the cells they are traversable through
%  i.e. traversable(B, U, D) and traversable(B, L, R) to show bridge B being traversable
%  only between the above and below cells, and the left and right cells respectively
% in a simple rectangle board, bridges are always traversable up/down and left/right, no other ways
% left/right (bridge cannot be on the left/right sides of the board)
traversable(B, C1, C2) :- bridge(B), cell(C1), cell(C2), x_size(XS), B-1=C1, B+1=C2, B\XS!=0, B\XS!=1, board_type(simple_rectangle).
% up/down
traversable(B, C1, C2) :- bridge(B), cell(C1), cell(C2), x_size(XS), B-XS=C1, B+XS=C2, board_type(simple_rectangle).
% reflexive
traversable(B, C2, C1) :- traversable(B, C1, C2), board_type(simple_rectangle).

% define cell number based on X Y predicate
cell_number(C, N) :- board_type(simple_rectangle), cell(C), num_at(N, X, Y), C=X+((Y-1)*XS), x_size(XS).
