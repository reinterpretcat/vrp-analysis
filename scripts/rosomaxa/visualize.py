import numpy as np
import matplotlib.pyplot as plt

objectives = 3      # amount of objectives to be plotted
figsize = [12, 6]   # figure size, inches

# network state date from logs or metrics
(rows_min, rows_max, cols_min, cols_max, total_count, nodes) = data

node_map = {}
for node in nodes:
    (x, y, _, _, _, _) = node
    node_map[(x, y)] = node

# find max values in order to get min-max values
min_distance = 0
max_distance = 0
min_hits = 0
max_hits = 0
max_fitness = np.zeros(shape=objectives, dtype=np.float64)
min_fitness = np.full(shape=objectives, fill_value = np.finfo(np.float64).max, dtype=np.float64)
for y in range(cols_min, cols_max):
    for x in range(rows_min, rows_max):
        node = node_map.get((x, y))
        if node != None:
            (_, _, u_distance, hits, _, population) = node

            min_distance = min(min_distance, u_distance)
            max_distance = max(max_distance, u_distance)

            min_hits = min(min_hits, hits)
            max_hits = max(max_hits, hits)

            if len(population) > 0:
                min_fitness = np.minimum.reduce([min_fitness, population[0]])
                max_fitness = np.maximum.reduce([max_fitness, population[0]])

# create and fill matrices with data
cols = cols_max - cols_min + 1
rows = rows_max - rows_min + 1

u_matrix = np.zeros(shape=(rows, cols), dtype=np.float64)             # unified distance matrix
h_matrix = np.zeros(shape=(rows, cols), dtype=np.float64)             # hits matrix
o_matrix = np.zeros(shape=(rows, cols, objectives), dtype=np.float64) # objective fitness matrix

for y in range(cols_min, cols_max):
    for x in range(rows_min, rows_max):
        node = node_map.get((x, y))
        if node != None:
            (_, _, u_distance, hits, _, population) = node

            i = x - rows_min
            j = y - cols_min
            
            u_matrix[i][j] = u_distance
            h_matrix[i][j] = hits

            if len(population) > 0:
                o_matrix[i][j] = population[0]

# prepare and show plot
objective_matrices = np.array(list(map(lambda i: (F"objective_{i}", min_fitness[i], max_fitness[i], o_matrix[:, :, i]), range(0, objectives))))

matrices = dict(enumerate(np.concatenate(([("u_matrix", min_distance, max_distance, u_matrix), ("h_matrix", min_hits, max_hits, h_matrix)], objective_matrices))))

fig, ax = plt.subplots(nrows=1, ncols=max(objectives + 2, 2), figsize=figsize)
for i, axi in enumerate(ax.flat):
    plot_data = matrices.get(i)
    if plot_data != None:
        (title, min, max, matrix) = plot_data
        axi.set_title(title)
        axi.imshow(matrix, cmap='jet', vmin=min, vmax=max, interpolation='nearest')

plt.tight_layout(True)
plt.show()
