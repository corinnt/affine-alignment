import sys
from xml.etree.ElementPath import get_parent_map

class StringPair():
    def __init__(self, str_u, str_v) -> None:
        self.u = str_u
        self.v = str_v
        self.len_m = len(str_u) 
        self.len_n = len(str_v)

    def align_from_path(self, path):
        """ Method to reconstruct aligned strings from path through tables
            :param path: list[tuple] representing path from bottom right corner through tables
            Returns aligned string u, aligned string v
        """
        aligned_u, aligned_v = "", ""
        u_index = self.len_m - 1
        v_index = self.len_n - 1
        for direction in path:
            # append chars to aligned_v
            if direction[0] == -1:
                v_base = self.v[v_index]
                aligned_v = v_base + aligned_v
                v_index -= 1
            elif (direction[0] == 0 and direction[1] != 0):
                aligned_v = "-" + aligned_v
        # append chars to aligned_u
            if direction[1] == -1:
                u_base = self.u[u_index]
                aligned_u = u_base + aligned_u
                u_index -= 1
            elif (direction[1] == 0 and direction[0] != 0):
                aligned_u = "-" + aligned_u

        return aligned_u, aligned_v
    
class DPTables():
    def __init__(self) -> None:
        self.best = []
        self.diag = []
        self.u_gap = []
        self.v_gap = []
        self.backpointers = {}

    def final_score(self):
        """ Returns the final score : str in the bottom right of the overall/best DP table
            
        """
        return str(self.best[-1][-1])

class Scoring():
    def __init__(self, matrix_lines, open, extension) -> None:
        """ Scoring object to contain 
        """
        self.scoring_matrix =\
            [[item.strip() for item in line.split(" ") if item != ""]\
            for line in matrix_lines]
        self.matrix_i_dict =\
            {key:self.scoring_matrix[0].index(key)\
                for key in self.scoring_matrix[0]}

        self.open = open
        self.extension = extension

def parse_args():
    str_u = open(sys.argv[1],'r').readlines()[0].upper().strip()
    str_v = open(sys.argv[1],'r').readlines()[1].upper().strip()

    matrix_lines = open(sys.argv[2],'r').readlines()

    gap_open_penalty = int(sys.argv[3])
    gap_ext_penalty = int(sys.argv[4])

    strings = StringPair(str_u, str_v)
    scoring = Scoring(matrix_lines, gap_open_penalty, gap_ext_penalty)
    return strings, scoring

def instantiate_dp_tables(strings : StringPair, tables : DPTables, scoring : Scoring):
    tables_list = [tables.best, tables.diag, tables.u_gap, tables.v_gap]
    for table in tables_list:
        table = [[0 for _ in range(strings.len_m + 1)] for _ in range(strings.len_n + 1)]
    # POSSBUG: are these by pointer or value? grayed out as unused var
    for i in range(3): tables.backpointers[(0, 0, i + 1)] = (0, 0, 0)
    instantiate_table_edges(tables, tables, scoring)

#instantiate top row and left column of dp_tables + add pointers to dict
def instantiate_table_edges(strings : StringPair, tables : DPTables, scoring : Scoring):
    for i in range(1, strings.len_m + 1): 
        tables.best[0][i] = ( + (i * scoring.extension))
        tables.v_gap[0][i] = (scoring.open + (i * scoring.extension))
        tables.u_gap[0][i] = float('-inf')
        tables.backpointers[(0, i, 0)] = (0, -1, 0)
        tables.backpointers[(0, i, 2)] = (0, -1, 2)
    for j in range(1, strings.len_n + 1):
        tables.best[j][0] = (scoring.open + (j * scoring.extension))
        tables.u_gap[j][0] = (scoring.open + (j * scoring.extension))
        tables.v_gap[j][0] = float('-inf')
        tables.backpointers[(j, 0, 0)] = (-1, 0, 0)
        tables.backpointers[(j, 0, 3)] = (-1, 0, 3)


def fill_dp_tables(strings, tables, scoring):
    """ Perform DP calculations for optimal alignment 
        while adding backpointers to dictionary to reconstruct path through tables
    """
    for j in range(1, strings.len_n + 1):
        for i in range(1, strings.len_m + 1):
            u_mat_index = scoring.matrix_i_dict[strings.u[i - 1]]
            v_mat_index = scoring.matrix_i_dict[strings.v[j - 1]]
            matrix_score = int(scoring.scoring_matrix[u_mat_index][v_mat_index])

            diag = tables.best[j - 1][i - 1] + matrix_score

            open_up_cost = tables.best[j - 1][i] + scoring.extension + scoring.open
            extend_up_cost = tables.v_gap[j - 1][i] + scoring.extension
            if open_up_cost > extend_up_cost:
                up = open_up_cost
                # point from j, i dp_table_v_gap to dp_table_best j - 1, i
                tables.backpointers[(j, i, 2)] = (- 1, 0, 0)
            else: 
                up = extend_up_cost
                # point from j, i dp_table_v_gap to dp_table_v_gap j - 1, i
                tables.backpointers[(j, i, 2)] = (- 1, 0, 2)

            open_left_cost = tables.best[j][i - 1] + scoring.extension + scoring.open
            extend_left_cost = tables.u_gap[j][i - 1] + scoring.extension
            if open_left_cost > extend_left_cost:
                left = open_left_cost
                # point from j, i dp_table_u_gap to dp_table_best j, i - 1
                tables.backpointers[(j, i, 3)] = (0, - 1, 0)
            else: 
                left = extend_left_cost
                # point from j, i dp_table_u_gap to dp_table_u_gap j, i - 1
                tables.backpointers[(j, i, 3)] = (0, - 1, 3)
         
        # update all sub dp_tables
            tables.diag[j][i] = diag 
            tables.v_gap[j][i] = up
            tables.u_gap[j][i] = left

        # update main dp_table
            new_val = max(diag, up, left)
            tables.best[j][i] = new_val

            if new_val == diag:
                direction = (-1, -1, 0) # got val from dp_table_diag
            elif new_val == up:
                direction = (-1, 0, 2) # got val from dp_table_v_gap
            else:
                direction = (0, -1, 3) # got val from dp_table_u_gap
            tables.backpointers[(j, i, 0)] = direction
            tables.backpointers[(j, i, 1)] = (-1, -1, 0)

def find_path(strings, tables):
    """ Given a StringPair and DPTables, returns a list[tuples]
        representing the path to the optimal score through the dptables
    """ 
# backtracking
    curr_position = (strings.len_n, strings.len_m, 0)
    path = []
    while (curr_position != (0, 0, 0)):
        direction = tables.backpointers[curr_position]
        path.append(direction)
        curr_position =\
        (curr_position[0] + direction[0],\
        curr_position[1] + direction[1],\
        direction[2])
    return path

def main():
    tables = DPTables()
    instantiate_dp_tables(tables)
    strings, scoring = parse_args()
    fill_dp_tables(tables, scoring)
    path : list[tuple] = find_path(strings, scoring)
    aligned_u, aligned_v = strings.align_from_path(path)
    sys.stdout.write(aligned_u + '\n')
    sys.stdout.write(aligned_v  + '\n')
    sys.stdout.write(tables.final_score() + '\n')

if __name__ == "__main__":
    main()