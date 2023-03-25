import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.safes = set()
        self.mines = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes
    
    def unknown(self):
        return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            if self.count<1:
                return False
            else:
                self.cells.remove(cell)
                self.mines.add(cell)
                self.count -= 1
                return True
        else:
            return True

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            if len(self.cells)  < self.count:
                return False
            else:
                self.cells.remove(cell)
                self.safes.add(cell)
                return True
        else:
            return True

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()
        self.availiable = [(i,j) for i in range(height) for j in range(width)]
        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()
        
        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
    
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.availiable.remove(cell)
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
        x,y = cell
        add_cells = []
        for i in range(max(0,x-1),min(x+2,self.height)):
            for j in range(max(0,y-1),min(y+2,self.width)):
                add_cells.append((i,j))
        new_sentence = Sentence(add_cells,count)
        for scell in add_cells:
            if scell in self.safes:
                new_sentence.mark_safe(scell)
            if scell in self.mines:
                new_sentence.mark_mine(scell)
        self.knowledge.append(new_sentence)
        todo_list = self.knowledge.copy()
        updated_list = []
        safes = []
        mines = []
        while len(todo_list):
            ref = todo_list.pop()
            #print("Pop point: ",ref)
            tobe_add = []
            tobe_remove = []
            if ref.count==0:
                for tmp_cell in ref.cells:
                    for kwlg in todo_list:
                        kwlg.mark_safe(tmp_cell)
                    safes.append(tmp_cell)
                    #self.mark_safe(tmp_cell)
                continue
            elif len(ref.cells)==ref.count:
                for tmp_cell in ref.cells:
                    for kwlg in todo_list:
                        kwlg.mark_mine(tmp_cell)
                    mines.append(tmp_cell)
                    #self.mark_mine(tmp_cell)
                continue
            elif len(ref.cells)==0:
                continue
            orth = True
            for stc in todo_list:
                if ref.cells.issubset(stc.cells):
                    if ref!=stc:
                        tobe_add.append(Sentence(stc.cells - ref.cells,stc.count - ref.count))
                        tobe_remove.append(stc)
                    else:
                        tobe_remove.append(stc)
                elif stc.cells.issubset(ref.cells):
                    orth = False
                    tobe_add.append(Sentence(ref.cells - stc.cells,ref.count - stc.count))
            
            if orth:
                updated_list.append(ref)
            for rm in tobe_remove:
                todo_list.remove(rm)
            for ad in tobe_add:
                todo_list.append(ad)
        for safecell in safes:
            self.mark_safe(safecell)
        for minecell in mines:
            self.availiable.remove(minecell)
            self.mark_mine(minecell)
        print("Safes: ",self.safes)
        print("Mines: ",self.mines)
        self.knowledge = updated_list
        print("Knowledge")
        for kwlg in self.knowledge:
            print(kwlg)
                    
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for i in range(self.width):
            for j in range(self.height):
                if (i,j) not in self.moves_made and (i,j) in self.safes:
                    return (i,j)
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.availiable):
            return self.availiable[random.randint(0,len(self.availiable)-1)]
        else:
            print("Done!")
