import utils as ut

row_units = [ut.cross(r, ut.cols) for r in ut.rows]
column_units = [ut.cross(ut.rows, c) for c in ut.cols]
square_units = [ut.cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
unitlist = row_units + column_units + square_units

# Update the unit list to add the new diagonal units
unitlist = unitlist + [[ut.rows[i] + ut.cols[i] for i in range(9)]] + [[ut.rows[::-1][i] + ut.cols[i] for i in range(9)]]

# Must be called after all units (including diagonals) are added to the unitlist
units = ut.extract_units(unitlist, ut.boxes)
peers = ut.extract_peers(units, ut.boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).

    """
    twins = set()

    for unit_id, unit in enumerate(unitlist):
        two = [(box, values[box]) for box in unit if len(values[box]) == 2]
        two = sorted(two, key=lambda tup: tup[1])
        for i in range(len(two)-1):
            q = []
            if two[i][1] == two[i+1][1] and two[i][1] not in q:
                q.append(two[i][1])
                twins.add((unit_id, two[i][0], two[i+1][0], two[i][1]))

    for unit_id, box1, box2, value in twins:
        for box in unitlist[unit_id]:
            if box in [box1, box2]:
                continue
            values[box] = values[box].replace(value[0], '')
            values[box] = values[box].replace(value[1], '')

    return values


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers

    """
    box = [b for b in values.keys() if len(values[b]) == 1]
    for b in box:
        for peer in peers[b]:
            values[peer] = values[peer].replace(values[b], '')
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom

    """
    for unit in unitlist:
        for i in range(9):
            count = [1 if str(i+1) in values[unit[idx]] else 0 for idx in range(9)]
            if sum(count) == 1:
                idx = count.index(1)
                values[unit[idx]] = str(i+1)
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable

    """
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.

    """
    values = reduce_puzzle(values)

    if not values:
        return False

    if len([box for box in values.keys() if len(values[box]) == 1]) == 9**2:
        return values
    _, box = min((len(values[box]), box) for box in values.keys() if len(values[box]) > 1)

    for value in values[box]:
        values_copy1 = values.copy()
        values_copy1[box] = value
        values_copy2 = search(values_copy1)

        if values_copy2:
            return values_copy2


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.

    """
    values = ut.grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    ut.display(ut.grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    ut.display(result)

    try:
        import PySudoku
        PySudoku.play(ut.grid2values(diag_sudoku_grid), result, ut.history)

    except SystemExit:
        pass

    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
