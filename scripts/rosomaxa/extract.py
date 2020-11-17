import numpy as np
import sys


def get_matrices(data, objectives, weights, rows_min=sys.maxsize, rows_max=-sys.maxsize, cols_min=sys.maxsize, cols_max=-sys.maxsize):
    # network state date from logs or metrics
    (data_rows_min, data_rows_max, data_cols_min,
     data_cols_max, total_count, nodes) = data

    rows_min = min(rows_min, data_rows_min)
    rows_max = max(rows_max, data_rows_max)
    cols_min = min(cols_min, data_cols_min)
    cols_max = max(cols_max, data_cols_max)

    node_map = {}
    for node in nodes:
        (x, y, _, _, _, _, _) = node
        node_map[(x, y)] = node

    # find max values in order to get min-max values
    min_distance = 0
    max_distance = 0
    min_thits = 0
    max_thits = 0
    min_lhits = 0
    max_lhits = 0
    max_fitness = np.zeros(shape=objectives, dtype=np.float64)
    min_fitness = np.full(shape=objectives, fill_value=np.finfo(
        np.float64).max, dtype=np.float64)
    max_weights = np.zeros(shape=weights, dtype=np.float64)
    min_weights = np.full(shape=weights, fill_value=np.finfo(
        np.float64).max, dtype=np.float64)
    for y in range(cols_min, cols_max):
        for x in range(rows_min, rows_max):
            node = node_map.get((x, y))
            if node != None:
                (_, _, u_distance, total_hits, last_hits, weights_values, population) = node

                min_distance = min(min_distance, u_distance)
                max_distance = max(max_distance, u_distance)

                min_thits = min(min_thits, total_hits)
                max_thits = max(max_thits, total_hits)

                min_lhits = min(min_lhits, last_hits)
                max_lhits = max(max_lhits, last_hits)

                min_weights = np.minimum.reduce([min_weights, weights_values])
                max_weights = np.maximum.reduce([max_weights, weights_values])

                if len(population) > 0:
                    min_fitness = np.minimum.reduce(
                        [min_fitness, population[0]])
                    max_fitness = np.maximum.reduce(
                        [max_fitness, population[0]])

    # create and fill matrices with data
    cols = cols_max - cols_min + 1
    rows = rows_max - rows_min + 1

    # unified distance matrix
    u_matrix = np.zeros(shape=(rows, cols), dtype=np.float64)
    # total hits matrix
    t_matrix = np.zeros(shape=(rows, cols), dtype=np.float64)
    # last hits matrix
    l_matrix = np.zeros(shape=(rows, cols), dtype=np.float64)
    # objective fitness matrix
    o_matrix = np.zeros(shape=(rows, cols, objectives), dtype=np.float64)
    # weights matrix
    w_matrix = np.zeros(shape=(rows, cols, weights), dtype=np.float64)

    for y in range(cols_min, cols_max):
        for x in range(rows_min, rows_max):
            node = node_map.get((x, y))
            if node != None:
                (_, _, u_distance, total_hits, last_hits, weights_values, population) = node

                i = x - rows_min
                j = y - cols_min

                u_matrix[i][j] = u_distance
                t_matrix[i][j] = total_hits
                l_matrix[i][j] = last_hits
                w_matrix[i][j] = weights_values

                if len(population) > 0:
                    o_matrix[i][j] = population[0]

    # prepare plot data
    objective_matrices = np.array(list(map(lambda i: (
        F"objective_{i}", min_fitness[i], max_fitness[i], o_matrix[:, :, i]), range(0, objectives))))

    weights_matrices = np.array(list(map(lambda i: (
        F"weight_{i}", min_weights[i], max_weights[i], w_matrix[:, :, i]), range(0, weights))))

    return dict(enumerate(np.concatenate(([
        ("u_matrix", min_distance, max_distance, u_matrix),
        ("t_matrix", min_thits, max_thits, t_matrix),
        ("l_matrix", min_lhits, max_lhits, l_matrix)
    ], objective_matrices, weights_matrices))))
