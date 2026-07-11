import clyngor
from clyngor import solve

import tkinter
from tkinter import ttk

from enum import Enum

# boardtype enum
class BoardType(Enum):
    SIMPLE_RECTANGLE = 'Simple Rectangle'

BOARD_TYPES = []
for e in BoardType:
    BOARD_TYPES.append(e.value)

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

# translation dictionary to convert typing letters into relevant colors
#   most useful to help in visualizing an actual flow puzzle solution
char2num = {
    'r': 1, 'R': 1, # red
    'g': 10, 'G': 2, # gray/green
    'o': 8, 'O': 3, # brown/orange
    'y': 4, 'Y': 4, # yellow
    'p': 5, 'P': 9, # pink/purple
    'c': 7, 'C': 6, # cyan/blue
}

class SolverGui:
    root = tkinter.Tk()
    root.title("Number Link Solver")

    # state tracking for the gui
    state = {
        'xSize': tkinter.IntVar(value=5),
        'ySize': tkinter.IntVar(value=5),
        'board': [],
        'walls': [],
        'wallLineIds': {},
        'threads': tkinter.IntVar(value=1),
        'lastStats': {},
        'boardType': tkinter.StringVar(value=BoardType.SIMPLE_RECTANGLE.value),
        'constantElements': set(),
        'boardFrame': None,
        'canvas': None,
    }

    # holds controls on the left and board frame on the right
    mainFrame = ttk.Frame(root, padding=10)
    mainFrame.grid()

    # external function to start the gui
    def startGui(self):
        self.__firstInit()
        self.__initGui()
        self.root.mainloop()

    # initialize consistent gui elements
    def __firstInit(self):
        def save(element):
            self.state['constantElements'].add(element)

        # holds the board, rendering changing based on board type
        boardFrame = ttk.Frame(self.mainFrame)
        boardFrame.grid(column=3, row=0, rowspan=12)
        self.state['boardFrame'] = boardFrame
        save(boardFrame)

        # canvas within the board frame, rendering changing based on board type
        canvas = tkinter.Canvas(boardFrame, bg='white')
        canvas.grid(columnspan=1000, rowspan=1000)
        self.state['canvas'] = canvas
        canvas.bind("<Button-1>", self.__canvasClick)
        save(canvas) # probably unnecessary

        boardTypeVar = self.state['boardType']
        boardTypeSelect = ttk.Combobox(self.mainFrame, values=BOARD_TYPES, textvariable=boardTypeVar)
        boardTypeSelect.grid(column=0, row=0)
        save(boardTypeSelect)
        boardTypeVar.trace_add('write', self.__initGui)

        threadLabel = ttk.Label(self.mainFrame, text="Solving Threads:")
        threadLabel.grid(column=0, row=7)
        save(threadLabel)

        threadEntry = ttk.Entry(self.mainFrame, textvariable=self.state["threads"], width=5)
        threadEntry.grid(column=0, row=8)
        save(threadEntry)

        lastRunStatsBtn = ttk.Button(self.mainFrame, text="Last Run Stats", command=self.__printLastStats)
        lastRunStatsBtn.grid(column=0, row=9)
        save(lastRunStatsBtn)

        clearBoardBtn = ttk.Button(self.mainFrame, text="Clear", command=self.__makeBlankBoard)
        clearBoardBtn.grid(column=0, row=10)
        save(clearBoardBtn)

        solveBtn = ttk.Button(self.mainFrame, text="Solve", command=self.__solveBoard)
        solveBtn.grid(column=0, row=11)
        save(solveBtn)

        # update the gui board every time the size is changed, and generate one to start
        self.state['xSize'].trace_add('write', self.__makeBlankBoard)
        self.state['ySize'].trace_add('write', self.__makeBlankBoard)
        self.__makeBlankBoard()

        # static label describing color coersion
        colorLabelStr = "R/r=red; G=green, g=gray; O=orange, o=brown; Y/y=yellow; P=purple, p=pink; C=blue, c=cyan\n\nB/b=bridge; E/e=excluded"
        colorLabel = ttk.Label(self.mainFrame, text=colorLabelStr, justify='center', wraplength=150)
        colorLabel.grid(column=3, row=13)
        save(colorLabel)

    # initializes the gui based on the board type state
    def __initGui(self, *args):
        # remove everything that's not constant
        for child in self.mainFrame.winfo_children():
            if child not in self.state['constantElements']:
                child.destroy()
        
        # add elements based on board type
        match self.state['boardType'].get():
            case BoardType.SIMPLE_RECTANGLE.value:
                ttk.Label(self.mainFrame, text="X Size:").grid(column=0, row=1)
                ttk.Entry(self.mainFrame, textvariable=self.state["xSize"], width=5).grid(column=0, row=2)

                ttk.Label(self.mainFrame, text="Y Size:").grid(column=0, row=3)
                ttk.Entry(self.mainFrame, textvariable=self.state["ySize"], width=5).grid(column=0, row=4)

    # called whenever the canvas beneath the board is clicked
    def __canvasClick(self, event):
        match self.state['boardType'].get():
            case BoardType.SIMPLE_RECTANGLE.value:
                # X: 2 canvas - 18 entry - 4 canvas - 18 entry - 4 canvas - 18 entry - 4 canvas - ... - 18 entry - 2 canvas
                # Y: 2 canvas - 21 entry - 4 canvas - 21 entry - 4 canvas - 21 entry - 4 canvas - ... - 21 entry - 2 canvas
                x = event.x; y = event.y

                # don't allow clicks on the left/top
                if x >= 3 and y >= 3:
                    xSize = self.state["xSize"].get()
                    ySize = self.state["ySize"].get()

                    xColLeft = (x-2) // 22
                    yRowTop = (y-2) // 25

                    canvas = self.state['canvas']

                    # holder to use the same create line
                    x0, y0, x1, y1 = 0, 0, 0, 0

                    wallToBe = None

                    # now detect if we're doing a horizontal or vertical wall
                    if (y - 2) % 25 < 21 and xColLeft + 1 < xSize: # horizontal wall
                        wallToBe = (xColLeft, yRowTop, xColLeft+1, yRowTop)
                        x0=(xColLeft*22)+22; x1=x0; y0=(yRowTop*25); y1=y0+25
                    elif (x - 2) % 22 < 18 and yRowTop + 1 < ySize: # vertical wall
                        wallToBe = (xColLeft, yRowTop, xColLeft, yRowTop+1)
                        x0=(xColLeft*22); x1=x0+22; y0=(yRowTop*25)+25; y1=y0

                    if wallToBe != None:
                        walls = self.state['walls']
                        wallIds = self.state['wallLineIds']
                        
                        if wallToBe in walls:
                            walls.remove(wallToBe)
                            canvas.delete(wallIds[wallToBe])
                        else:
                            walls.append(wallToBe)
                            wallIds[wallToBe] = canvas.create_line(x0, y0, x1, y1, fill='red', width=5)

                print(event.x, event.y)

    # clears all lines from the canvas
    def __clearCanvas(self):
        self.state['canvas'].delete('all')
        self.state['walls'] = []
        self.state['wallLineIds'] = {}

    # clears all the number links from the canvas
    def __clearFlows(self):
        self.state['canvas'].delete("NumberLink")

    # clears the current grid of entries and generates a new one sized to the 2d board array in gui state
    def __displayBoard(self, *args):
        board = self.state["board"]
        board: list[list[tkinter.StringVar]] 

        boardFrame = self.state['boardFrame']
        canvas = self.state['canvas']

        # destroy all the existing entries; leave the canvas
        for child in boardFrame.winfo_children():
            if not isinstance(child, tkinter.Canvas):
                child.destroy()

        match self.state['boardType'].get():
            case BoardType.SIMPLE_RECTANGLE.value:
                # xSize and ySize are used to resize the canvas; they're handled in the loop because they can be
                xSize, ySize = 0, 0
                for row in range(len(board)):
                    ySize = row + 1
                    for col in range(len(board[row])):
                        xSize = col + 1
                        textFrame = ttk.Frame(boardFrame, width=18, height=21)
                        textFrame.grid(column=col, row=row, padx=2, pady=2)
                        textFrame.grid_propagate(False)
                        ttk.Entry(textFrame, textvariable=board[row][col]).grid(sticky=tkinter.NE)

                # magic numbers correctly size the canvas to only extend as required to cover the entry grid
                canvas.configure(width=xSize*22, height=ySize*25)

    # calls relevant blank board function based on board state
    def __makeBlankBoard(self, *args):
        match self.state['boardType'].get():
            case BoardType.SIMPLE_RECTANGLE.value:
                self.__makeBlankRectangleBoard(args)

    # creates a 2d array board of StringVars and stores in the the state dictionary for gui display
    #   secondary effects: clears current values in the board and erases all drawn lines
    def __makeBlankRectangleBoard(self, *args):
        xSize, ySize = 0, 0
        
        # without this try-catch an error is thrown whenever the text boxes are blank
        #  (even for a microsecond when replacing a full number by selecting and typing)
        try:
            xSize = self.state["xSize"].get()
            ySize = self.state["ySize"].get()
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
        self.state['board'] = board
        
        self.__clearCanvas()
        self.__displayBoard()

    # returns a tuple of a row and column from a cell id (using xSize from the gui state)
    #  assumes a simple rectangular grid
    def __cellToRowColIndex(self, cell) -> tuple[int, int]:
        xSize = self.state['xSize'].get()

        # floor division to find the row
        row = (cell-1) // xSize
        col = (cell-1) % xSize

        return (row, col)

    # draws a line in the gui between 2 provided cell ids
    #  number is used to pick a color for the line
    def __drawLine(self, cell1, cell2, number) -> None:
        pos0 = self.__cellToRowColIndex(cell1)
        pos1 = self.__cellToRowColIndex(cell2)

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

        self.state['canvas'].create_line(x0, y0, x1, y1, fill=color, width=5, tags=("NumberLink"))

    # simply prints the full stats of the last run to the console, rather than just time info
    def __printLastStats(self) -> None:
        print(self.state['lastStats'])

    # main solving function
    #  generates a facts file based on numbers entered into the gui
    #  runs the solver using this file
    #  uses the results of the solver to draw lines or announce unsatisfiability
    def __solveBoard(self):
        self.__clearFlows()

        boardType = self.state['boardType'].get()

        with open("_facts.lp", "w") as file:
            match boardType:
                case BoardType.SIMPLE_RECTANGLE.value:
                    file.write("board_type(simple_rectangle). ")
                    file.write(f"x_size({self.state['xSize'].get()}). ")
                    file.write(f"y_size({self.state['ySize'].get()}). ")

                    for wall in self.state['walls']:
                        file.write(f"wall_xy({wall[0]+1},{wall[1]+1},{wall[2]+1},{wall[3]+1}). ")

                    board = self.state['board']
                    for row in range(len(board)):
                        for col in range(len(board[row])):
                            # get the value in the GUI entry at the given row and column
                            #  note that rows and columns are 0 indexed in python but 1 indexed in the ASP code
                            n = board[row][col].get()

                            # bridges
                            if n in ["B", "b"]:
                                file.write(f"bridge_xy({col+1},{row+1}). ")
                            elif n in ["E", "e"]:
                                file.write(f"excluded_xy({col+1},{row+1}). ")
                            # not blank, check if it's a known char->num
                            elif n in char2num:
                                file.write(f"num_at({char2num[n]},{col+1},{row+1}). ")
                            # finally, try to treat it as a number
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

        # safe reading for thread count, default to 1
        threadCount = 1
        try:
            t = self.state['threads'].get()
            if t > 0:
                threadCount = t
        except:
            pass

        print('solving...')
        answers: clyngor.Answers = solve(files, nb_model=1, options=f'-t {threadCount}')

        # this is the line that gets stalled on during the solving process
        for answer in answers.by_predicate:
            print('solved')
            answer: dict[str, frozenset[tuple]]

            if boardType == BoardType.SIMPLE_RECTANGLE.value:
                board = self.state["board"]
                # this code is only relevant when running a pre-made fact file
                if "cell_number" in answer:
                    for cellNum in answer["cell_number"]:
                        pos = self.__cellToRowColIndex(cellNum[0])
                        board[pos[0]][pos[1]].set(cellNum[1])
                # this code is also only relevant when running a pre-made fact file
                if 'bridge' in answer:
                    for bridge in answer['bridge']:
                        pos = self.__cellToRowColIndex(bridge[0])
                        board[pos[0]][pos[1]].set("B")
                # draws a line for all of the connections
                if "edge_number" in answer:
                    for edgeNum in answer["edge_number"]:
                        self.__drawLine(edgeNum[0], edgeNum[1], edgeNum[2])
            break

        self.state['lastStats'] = answers.statistics
        print(f"Time: {answers.statistics['Time']}, CPU Time: {answers.statistics['CPU Time']}")

        # this has to be here, since the solving process happens on the above "answer in answers" line
        if answers.is_unsatisfiable:
            print('unsatisfiable')    

SolverGui().startGui()
