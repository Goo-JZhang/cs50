import sys

from crossword import *

import ipdb;

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains:
            for w in self.crossword.words:
                if len(w)!= v.length:
                    self.domains[v].remove(w)
                    

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        ret = False
        ovlp = self.crossword.overlaps[x,y]
        if ovlp is None:
            return False
        else:
            idx_x = ovlp[0]
            idx_y = ovlp[1]
            tobe_remove = set()
            for xword in self.domains[x]:
                find = False
                for yword in self.domains[y]:
                    if xword[idx_x]==yword[idx_y]:
                        find = True
                        break
                if find:
                    ret = True
                else:
                    tobe_remove.add(xword)
            for rmword in tobe_remove:
                self.domains[x].remove(rmword)
            return ret

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        not_empty = True
        if arcs is None:
            arcs = list()
            N = len(self.domains)
            varlist = list(self.domains.keys())
            for i in range(N):
                for j in range(i+1,N):
                    arcs.append((varlist[i],varlist[j]))
        for arc in arcs:
            if self.revise(*arc):
                if len(self.domains[arc[0]]) == 0:
                    not_empty = False
        return not_empty

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var,word in assignment.items():
            if len(word)!=var.length:
                return False
        N = len(assignment)
        varlist = list(assignment.keys())
        for i in range(N):
            for j in range(i+1,N):
                crosspoint = self.crossword.overlaps[varlist[i],varlist[j]]
                if crosspoint is None:
                    continue
                else:
                    idx_x = crosspoint[0]
                    idx_y = crosspoint[1]
                    if assignment[varlist[i]][idx_x]!=assignment[varlist[j]][idx_y]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        word_constraint = dict()
        assigned = set(assignment.keys())
        assigned.add(var)
        for word in self.domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var] = word
            if not self.consistent(new_assignment):
                continue
            word_constraint[word] = 0
            for v in self.domains:
                if v not in assigned:
                    crosspoint = self.crossword.overlaps[var,v]
                    if crosspoint is not None:
                        idx_x = crosspoint[0]
                        idx_y = crosspoint[1]
                        for vword in self.domains[v]:
                            if word[idx_x]!=vword[idx_y]:
                                word_constraint[word] += 1
                                break
        ret = sorted(word_constraint.items(),key = lambda x: x[1])
        ret = [x[0] for x in ret]
        return ret

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        domains_left = dict()
        for var in self.domains:
            if var not in assignment:
                domains_left[var] = self.domains[var].copy()
                for word in self.domains[var]:
                    for assign_var,assign_word in assignment.items():
                        crosspoint = self.crossword.overlaps[var,assign_var]
                        if crosspoint is not None:
                            idx_x = crosspoint[0]
                            idx_y = crosspoint[1]
                            if word[idx_x]!=assign_word[idx_y]:
                                domains_left[var].remove(word)
                                break
        sorted_var = sorted(domains_left.items(), key = lambda x: len(x[1]))
        #print("Unassigned:")
        #print(sorted_var)
        while len(sorted_var):
            if len(sorted_var[0][1]) == 0:
                sorted_var.pop(0)
            else:
                break
        if len(sorted_var) == 0:
            return None
        candidates = []
        for domains in sorted_var:
            if len(domains[1])==len(sorted_var[0][1]):
                candidates.append(domains)
        #print(assignment)
        #print(candidates)
        #print(" ")
        if len(candidates) == 1:
            return candidates[0][0]
        else:
            best_var = candidates[0][0]
            max_neighbors = 0
            for candidate in candidates:
                tmp_neighbors = len(sorted_var)
                for neighbor in sorted_var:
                    if candidate[0]!=neighbor[0]:
                        crosspoint = self.crossword.overlaps[candidate[0],neighbor[0]]
                        if crosspoint is not None:
                            idx_x = crosspoint[0]
                            idx_y = crosspoint[1]
                            joint_words = [(cw,nw) for cw in candidate[1] for nw in neighbor[1]]
                            for cw,nw in joint_words:
                                if cw[idx_x]!=nw[idx_y]:
                                    tmp_neighbors -= 1
                                    break
                if tmp_neighbors>max_neighbors:
                    best_var = candidate[0]
            return best_var         
                    
    def backtrack(self, assignment,depth = 0):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        try_var = self.select_unassigned_variable(assignment)
        if try_var is None:
            return None
        try_words = self.order_domain_values(try_var,assignment)
        new_assignment = assignment.copy()
        #print("    "*(len(assignment)-1),assignment)
        #print("    "*(len(assignment)-1),try_var,try_words)
        #ipdb.set_trace()
        for try_word in try_words:
            new_assignment[try_var] = try_word
            if self.consistent(new_assignment):
                #print(new_assignment)
                if self.assignment_complete(new_assignment):
                    return new_assignment
                else:
                    try_result = self.backtrack(new_assignment,depth+1)
                    #print(try_result)
                    if try_result is not None:
                        return try_result
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
