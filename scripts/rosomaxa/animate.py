import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from extract import get_matrices
from data import animation_data


objectives = 3      # amount of objectives to be plotted
figsize = [12, 6]   # figure size, inches


# determine grid size
rows_min=sys.maxsize
rows_max=-sys.maxsize
cols_min=sys.maxsize
cols_max=-sys.maxsize
for data in animation_data:
    (data_rows_min, data_rows_max, data_cols_min, data_cols_max, _, _) = data
    rows_min = min(rows_min, data_rows_min)
    rows_max = max(rows_max, data_rows_max)
    cols_min = min(cols_min, data_cols_min)
    cols_max = max(cols_max, data_cols_max)

animation_matrices = []
for data in animation_data:
    matrices = get_matrices(data, objectives, rows_min, rows_max, cols_min, cols_max)
    animation_matrices.append(matrices)


fig, ax = plt.subplots(nrows=1, ncols=max(objectives + 2, 2), figsize=figsize)

ims=[]
for i in range(0, len(animation_matrices)):
    for j, axi in enumerate(ax.flat):
        plot_data = animation_matrices[i].get(j)
        if plot_data != None:
            (title, min, max, matrix) = plot_data
            axi.set_title(title)
            im = axi.imshow(matrix, cmap='jet', vmin=min, vmax=max, interpolation='nearest')
            ims.append([im])


ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)
# ani.save('mwe.mp4')

plt.show()
