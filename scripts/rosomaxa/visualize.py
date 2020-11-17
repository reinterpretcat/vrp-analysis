import matplotlib.pyplot as plt
from extract import get_matrices
from data import animation_data

objectives = 3      # amount of objectives
weights = 5         # amount of weights
figsize = [12, 8]   # figure size, inches
plotsize = [2, 6]   # amout of subplots in plot

# network state date from logs or metrics
data = animation_data[0]

matrices = get_matrices(data, objectives, weights)

fig, ax = plt.subplots(nrows=plotsize[0], ncols=plotsize[1], figsize=figsize)
for i, axi in enumerate(ax.flat):
    plot_data = matrices.get(i)
    if plot_data != None:
        (title, min, max, matrix) = plot_data
        axi.set_title(title)
        min = min - (max - min) * 0.1
        axi.imshow(matrix, cmap='gist_earth', vmin=min, vmax=max)
    else:
        axi.set_visible(False)

plt.tight_layout(True)
plt.show()
