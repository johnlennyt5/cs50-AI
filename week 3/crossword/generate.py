import sys

from crossword import *


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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        # Step 1: Enforce node consistency
        self.enforce_node_consistency()

        # Step 2: Enforce arc consistency
        self.ac3()

        # Step 3: Begin backtracking search with an empty assignment
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Iterate over each variable in the crossword
        for var in self.crossword.variables:
            new_domain = set()

            # Check each word in the domain of the variable
            for word in self.domains[var]:
                # Remove words that do not satisfy unary constraints (length)
                if len(word) == var.length:
                    new_domain.add(word)
            self.domains[var] = new_domain

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
         # Initialize the variable to track whether a revision was made
        revised = False

        # Get the overlap indices between variables x and y
        overlap = self.crossword.overlaps[x, y]
        if overlap:
            i, j = overlap

            # Initialize a new set to store the updated domain of variable x
            new_domain = set()

            # Iterate over each word in the domain of variable x
            for val_x in self.domains[x]:
                # Check if there is any word in the domain of variable y that satisfies the overlap condition
                if any(val_x[i] == val_y[j] for val_y in self.domains[y]):
                    # If a satisfying word is found, add it to the new domain
                    new_domain.add(val_x)
                else:
                    # If no satisfying word is found, set revised to True
                    revised = True

            # Update the domain of variable x with the new_domain
            self.domains[x] = new_domain

        # Return whether a revision was made
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If arcs is not provided, initialize it with all possible arcs in the problem
        if arcs is None:
            arcs = [(var1, var2) for var1 in self.crossword.variables for var2 in self.crossword.neighbors(var1)]

        while arcs:
            x, y = arcs.pop(0)
            # Revise the domains of x and y based on arc consistency
            if self.revise(x, y):
                # If the domain of x becomes empty, the assignment is inconsistent
                if not self.domains[x]:
                    return False
                # Add new arcs for variables connected to x and not equal to y
                arcs.extend([(x, z) for z in self.crossword.neighbors(x) if z != y])
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check if each variable in the crossword has been assigned a value
        return all(var in assignment for var in self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words_set = set()
        for var, word in assignment.items():
            # Check for conflicts: repeated words or incorrect word lengths
            if word in words_set or len(word) != var.length:
                return False
            words_set.add(word)
            # Check for conflicts with neighbors
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if assignment[var][i] != assignment[neighbor][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Count the number of ruled-out values for each word in the domain
        ruled_out_counts = {word: 0 for word in self.domains[var]}
        for neighbor in self.crossword.neighbors(var):
            if neighbor not in assignment:
                i, j = self.crossword.overlaps[var, neighbor]
                for word in self.domains[var]:
                    for val_neighbor in self.domains[neighbor]:
                        # Check for conflicts with neighbors and increment ruled-out counts
                        if word[i] != val_neighbor[j]:
                            ruled_out_counts[word] += 1

        # Sort the domain values by the number of ruled-out values
        sorted_domain = sorted(self.domains[var], key=lambda word: ruled_out_counts[word])
        return sorted_domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = [var for var in self.crossword.variables if var not in assignment]
        # Sort unassigned variables by the number of remaining values and then by degree
        sorted_vars = sorted(unassigned_vars, key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var))))
        return sorted_vars[0] if sorted_vars else None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            # Check if the new assignment is consistent
            if self.consistent(new_assignment):
                # Recursively attempt to complete the assignment
                result = self.backtrack(new_assignment)
                if result:
                    return result

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
