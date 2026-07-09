import clyngor
from clyngor import solve

import tkinter
from tkinter import ttk

root = tkinter.Tk()
root.title("Number Link Solver")

# state tracking for the gui
state = {
    'xSize': tkinter.IntVar(value=5),
    'ySize': tkinter.IntVar(value=5),
    'board': [],
}

# colors to distinguish between up to 10 numbers
# all other numbers appear with black lines
num2color = {
    1: 'red',
    2: 'green',
    3: 'orange',
    4: 'yellow',
    5: 'pink',
    6: 'blue',
    7: 'cyan',
    8: 'brown',
    9: 'purple',
    10: 'gray',
}

# holds controls on the left and board frame on the right
mainFrame = ttk.Frame(root, padding=10)
mainFrame.grid()

# holds the grid of entries and the canvas for line drawing
boardFrame = ttk.Frame(mainFrame)
boardFrame.grid(column=3, row=0, rowspan=10)

# used to draw lines to showcase linkages
canvas = tkinter.Canvas(boardFrame, bg='white')
canvas.grid(columnspan=1000, rowspan=1000)

# clears all lines from the canvas
def clearCanvas():
    canvas.delete('all')

# clears the current grid of entries and generates a new one sized to the 2d board array in gui state
def displayBoard(*args):
    board = state["board"]
    board: list[list[tkinter.StringVar]] 

    # destroy all the existing entries; leave the canvas
    for child in boardFrame.winfo_children():
        if not isinstance(child, tkinter.Canvas):
            child.destroy()

    # xSize and ySize are used to resize the canvas; they're handled in the loop because they can be
    xSize, ySize = 0, 0
    for row in range(len(board)):
        ySize = row + 1
        for col in range(len(board[row])):
            xSize = col + 1
            ttk.Entry(boardFrame, textvariable=board[row][col], width=2).grid(column=col, row=row, padx=2, pady=2)

    # magic numbers correctly size the canvas to only extend as required to cover the entry grid
    canvas.configure(width=xSize*22, height=ySize*25)

# creates a 2d array board of StringVars and stores in the the state dictionary for gui display
#   secondary effects: clears current values in the board and erases all drawn lines
def makeBlankBoard(*args):
    xSize, ySize = 0, 0
    
    # without this try-catch an error is thrown whenever the text boxes are blank
    #  (even for a microsecond when replacing a full number by selecting and typing)
    try:
        xSize = state["xSize"].get()
        ySize = state["ySize"].get()
    except:
        return
    
    # catch and kill invalid data
    if xSize < 1 or ySize < 1:
        return
    
    # each row is the same size, so just create one to be copied
    row = []
    for _ in range(xSize):
        row.append(0)

    # then copy it as many times as required to make the full grid
    board = []
    for _ in range(ySize):
        board.append(row.copy())

    # then iterate the full grid and create string variables
    #  since each string variable has to be unique, and list.copy() is only a shallow copy
    for row in board:
        for i in range(len(row)):
            row[i] = tkinter.StringVar()
    
    # simply replace the board in the state
    state['board'] = board
    
    clearCanvas()
    displayBoard()

# returns a tuple of a row and column from a cell id (using xSize from the gui state)
#  assumes a simple rectangular grid
def cellToRowColIndex(cell) -> tuple[int, int]:
    xSize = state['xSize'].get()

    # floor division to find the row
    row = (cell-1) // xSize
    col = (cell-1) % xSize

    return (row, col)

# draws a line in the gui between 2 provided cell ids
#  number is used to pick a color for the line
def drawLine(cell1, cell2, number) -> None:
    pos0 = cellToRowColIndex(cell1)
    pos1 = cellToRowColIndex(cell2)

    # row=y, col=x
    #   magic numbers are pixel values to line up to the grid
    y0 = pos0[0]*25 + 12.5
    x0 = pos0[1]*22 + 11

    y1 = pos1[0]*25 + 12.5
    x1 = pos1[1]*22 + 11

    # black is the default color
    color = 'black'
    if number in num2color:
        color = num2color[number]

    canvas.create_line(x0, y0, x1, y1, fill=color, width=5)

# update the gui board every time the size is changed, and generate one to start
state['xSize'].trace_add('write', makeBlankBoard)
state['ySize'].trace_add('write', makeBlankBoard)
makeBlankBoard()

# main solving function
#  generates a facts file based on numbers entered into the gui
#  runs the solver using this file
#  uses the results of the solver to draw lines or announce unsatisfiability
def solve():
    clearCanvas()

    with open("_facts.lp", "w") as file:
        # the gui only works with simple rectangles
        file.write("board_type(simple_rectangle). ")
        file.write(f"x_size({state['xSize'].get()}). ")
        file.write(f"y_size({state['ySize'].get()}). ")

        board = state['board']
        for row in range(len(board)):
            for col in range(len(board[row])):
                # get the value in the GUI entry at the given row and column
                #  note that rows and columns are 0 indexed in python but 1 indexed in the ASP code
                n = board[row][col].get()

                # bridges
                if n in ["B", "b"]:
                    file.write(f"bridge_xy({col+1},{row+1}). ")
                # not blank, try to treat it as a number
                elif n != "":
                    try:
                        n = int(n)
                        file.write(f"num_at({n},{col+1},{row+1}). ")
                    except:
                        continue
                
    files = [
        "solver.lp",
        "simple_rectangle.lp",
        "_facts.lp",
    ]

    print('solving...')
    answers: clyngor.Answers = solve(files, nb_model=1)

    # this is the line that gets stalled on during the solving process
    for answer in answers.by_predicate:
        print('solved')
        answer: dict[str, frozenset[tuple]]

        if not "board_type" in answer:
            print('invalid answer set')
            break

        board_type = None
        for b in answer["board_type"]:
            board_type = b[0]
            break

        #print(answer)

        if board_type == "simple_rectangle":
            board = state["board"]
            # this code is only relevant when running a pre-made fact file
            for cellNum in answer["cell_number"]:
                pos = cellToRowColIndex(cellNum[0])
                board[pos[0]][pos[1]].set(cellNum[1])
            # draws a line for all of the connections
            for edgeNum in answer["edge_number"]:
                drawLine(edgeNum[0], edgeNum[1], edgeNum[2])
        break

    # this has to be here, since the solving process happens on the above "answer in answers" line
    if answers.is_unsatisfiable:
        print('unsatisfiable')

    print(answers.statistics)

ttk.Label(mainFrame, text="X Size:").grid(column=0, row=0)
ttk.Entry(mainFrame, textvariable=state["xSize"], width=5).grid(column=0, row=1)

ttk.Label(mainFrame, text="Y Size:").grid(column=0, row=2)
ttk.Entry(mainFrame, textvariable=state["ySize"], width=5).grid(column=0, row=3)

ttk.Button(mainFrame, text="Clear", command=makeBlankBoard).grid(column=0, row=8)
ttk.Button(mainFrame, text="Solve", command=solve).grid(column=0, row=9)

root.mainloop()