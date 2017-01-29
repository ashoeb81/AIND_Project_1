assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    a_cross_b = [s + t for s in A for t in B]
    return a_cross_b

# Constants definition
ROWS = 'ABCDEFGHI'  # Rows of 9x9 sudoku
COLS = '123456789'  # Columns of 9x9 sudoku
BOXES = cross(ROWS, COLS)  # All 81 squares of sudoku board
ROW_UNITS = [cross(r, COLS) for r in ROWS]  # List of Row units.
COLUMN_UNITS = [cross(ROWS, c) for c in COLS]  # List of Column units.
SQUARE_UNITS = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]  # List of 3X3 square units
LEFT_TO_RIGHT_DIAG_UNIT = [['%s%s' % (a,b) for a,b in zip(list(ROWS), list(COLS))]]   # Left-to-Right Diagonal.
RIGHT_TO_LEFT_DIAG_UNIT = [['%s%s' % (a,b) for a,b in zip(list(ROWS), list(COLS)[::-1])]]  # Right-to-Left Diagonal.
DIAG_UNITS = LEFT_TO_RIGHT_DIAG_UNIT + RIGHT_TO_LEFT_DIAG_UNIT  # List of diagonal units.
UNITLIST = ROW_UNITS + COLUMN_UNITS + SQUARE_UNITS + DIAG_UNITS  # All units.
UNITS_DICT = dict((s, [u for u in UNITLIST if s in u]) for s in BOXES)  # Dictionary mapping box to units.
PEERS_DICT = dict((s, set(sum(UNITS_DICT[s],[]))-set([s])) for s in BOXES)  # Dictionary mapping box to peers.


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    grid = dict(zip(BOXES, grid))
    for k, v in grid.items():
        if v == '.':
            grid[k] = '123456789'
    return grid


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in BOXES)
    line = '+'.join(['-'*(width*3)]*3)
    for r in ROWS:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in COLS))
        if r in 'CF': print(line)
    return


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in UNITLIST:
        # Find all boxes with two digit choices in the unit under consideration.  These are naked twin candidates.
        candidates = [box for box in unit if len(values[box]) == 2]
        # Pair together boxes that have the same two choices for digits.  These are naked twins.
        paired_candidates = [(a, b) for a in candidates for b in candidates if a != b and values[a] == values[b]]
        # For each set of naked twins, remove naked twins values from all peers in the unit.
        # Loop over naked twins
        for pair in paired_candidates:
            # Loop over peers in the current unit.
            for box in unit:
                if box not in pair:
                    # Remove each value of naked twins from peer.
                    for digit in values[pair[0]]:
                        values = assign_value(values, box, values[box].replace(digit, ''))
    return values



def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in PEERS_DICT[box]:
            values = assign_value(values, peer, values[peer].replace(digit,''))
    return values



def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    new_values = values.copy()  # note: do not modify original values
    for unit in UNITLIST:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                new_values = assign_value(new_values, dplaces[0], digit)
    return new_values




def reduce_puzzle(values):
    """
    Iterate eliminate(), only_choice(), and naked_twins(). If at some point, there is a box with no
      available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values




def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in BOXES):
        return values  ## Solved!
    # Chose one of the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in BOXES if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku = assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt



def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Convert string representation of sudoku to dictionary representation.
    grid_dict = grid_values(grid)
    # Perform constraint propagation and search.
    solution = search(grid_dict)
    return solution



if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
