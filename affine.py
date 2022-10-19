import sys
from xml.etree.ElementPath import get_parent_map

str_u = open(sys.argv[1],'r').readlines()[0].upper().strip()
str_v = open(sys.argv[1],'r').readlines()[1].upper().strip()

matrix_lines = open(sys.argv[2],'r').readlines()

gap_open_penalty = int(sys.argv[3])
gap_ext_penalty = int(sys.argv[4])

len_m = len(str_u) 
len_n = len(str_v)

scoring_matrix =\
    [[item.strip() for item in line.split(" ") if item != ""]\
      for line in matrix_lines]

matrix_i_dict =\
    {key:scoring_matrix[0].index(key)\
     for key in scoring_matrix[0]}

dp_table_best = [[0 for _ in range(len_m + 1)] for _ in range(len_n + 1)]
dp_table_diag = [[0 for _ in range(len_m + 1)] for _ in range(len_n + 1)]
dp_table_u_gap = [[0 for _ in range(len_m + 1)] for _ in range(len_n + 1)]
dp_table_v_gap = [[0 for _ in range(len_m + 1)] for _ in range(len_n + 1)]

dp_table_best[0][0] = 0
backpointers_dict = {}
backpointers_dict[(0, 0, 1)] = (0, 0, 0)
backpointers_dict[(0, 0, 2)] = (0, 0, 0)
backpointers_dict[(0, 0, 3)] = (0, 0, 0)

#instantiate top row and left column of dp_tables + add pointers to dict
def instantiate_table_edges():
    for i in range(1, len_m + 1): 
        dp_table_best[0][i] = (gap_open_penalty + (i * gap_ext_penalty))
        dp_table_v_gap[0][i] = (gap_open_penalty + (i * gap_ext_penalty))
        dp_table_u_gap[0][i] = float('-inf')
        backpointers_dict[(0, i, 0)] = (0, -1, 0)
        backpointers_dict[(0, i, 2)] = (0, -1, 2)
    for j in range(1, len_n + 1):
        dp_table_best[j][0] = (gap_open_penalty + (j * gap_ext_penalty))
        dp_table_u_gap[j][0] = (gap_open_penalty + (j * gap_ext_penalty))
        dp_table_v_gap[j][0] = float('-inf')
        backpointers_dict[(j, 0, 0)] = (-1, 0, 0)
        backpointers_dict[(j, 0, 3)] = (-1, 0, 3)

# fill in body of dp_table_best + add pointers to dict
def fill_dp_tables():
    for j in range(1, len_n + 1):
        for i in range(1, len_m + 1):
            u_mat_index = matrix_i_dict[str_u[i - 1]]
            v_mat_index = matrix_i_dict[str_v[j - 1]]
            matrix_score = int(scoring_matrix[u_mat_index][v_mat_index])

            diag = dp_table_best[j - 1][i - 1] + matrix_score

            open_up_cost = dp_table_best[j - 1][i] + gap_ext_penalty + gap_open_penalty
            extend_up_cost = dp_table_v_gap[j - 1][i] + gap_ext_penalty
            if open_up_cost > extend_up_cost:
                up = open_up_cost
                # point from j, i dp_table_v_gap to dp_table_best j - 1, i
                backpointers_dict[(j, i, 2)] = (- 1, 0, 0)
            else: 
                up = extend_up_cost
                # point from j, i dp_table_v_gap to dp_table_v_gap j - 1, i
                backpointers_dict[(j, i, 2)] = (- 1, 0, 2)

            open_left_cost = dp_table_best[j][i - 1] + gap_ext_penalty + gap_open_penalty
            extend_left_cost = dp_table_u_gap[j][i - 1] + gap_ext_penalty
            if open_left_cost > extend_left_cost:
                left = open_left_cost
                # point from j, i dp_table_u_gap to dp_table_best j, i - 1
                backpointers_dict[(j, i, 3)] = (0, - 1, 0)
            else: 
                left = extend_left_cost
                # point from j, i dp_table_u_gap to dp_table_u_gap j, i - 1
                backpointers_dict[(j, i, 3)] = (0, - 1, 3)
         
        # update all sub dp_tables
            dp_table_diag[j][i] = diag 
            dp_table_v_gap[j][i] = up
            dp_table_u_gap[j][i] = left

        # update main dp_table
            new_val = max(diag, up, left)
            dp_table_best[j][i] = new_val

            if new_val == diag:
                direction = (-1, -1, 0) # got val from dp_table_diag
            elif new_val == up:
                direction = (-1, 0, 2) # got val from dp_table_v_gap
            else:
                direction = (0, -1, 3) # got val from dp_table_u_gap
            backpointers_dict[(j, i, 0)] = direction
            backpointers_dict[(j, i, 1)] = (-1, -1, 0)

def find_path():
# backtracking
    curr_position = (len_n, len_m, 0)
    path = []
    while (curr_position != (0, 0, 0)):
        direction = backpointers_dict[curr_position]
        path.append(direction)
        curr_position =\
        (curr_position[0] + direction[0],\
        curr_position[1] + direction[1],\
        direction[2])
    return path
    #translating dp_table path to alignments
aligned_u = ""
aligned_v = ""
u_index = len_m - 1
v_index = len_n - 1

#iterating through path which is already in reverse order
def align_strings_from_path(path):
    aligned_u = ""
    aligned_v = ""
    u_index = len_m - 1
    v_index = len_n - 1
    for direction in path:
        # append chars to aligned_v
        if direction[0] == -1:
            v_base = str_v[v_index]
            aligned_v = v_base + aligned_v
            v_index -= 1
        elif (direction[0] == 0 and direction[1] != 0):
            aligned_v = "-" + aligned_v

    # append chars to aligned_u
        if direction[1] == -1:
            u_base = str_u[u_index]
            aligned_u = u_base + aligned_u
            u_index -= 1
        elif (direction[1] == 0 and direction[0] != 0):
            aligned_u = "-" + aligned_u
        
    return aligned_u, aligned_v

def main():
    instantiate_table_edges()
    fill_dp_tables()
    path : list[tuple] = find_path()
    aligned_u, aligned_v = align_strings_from_path(path)
    sys.stdout.write(aligned_u + '\n')
    sys.stdout.write(aligned_v  + '\n')
    sys.stdout.write(str(dp_table_best[len_n][len_m]) + '\n')

if __name__ == "__main__":
    main()