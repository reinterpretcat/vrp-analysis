import matplotlib.pyplot as plt
from extract import get_matrices
from data import animation_data

objectives = 3      # amount of objectives to be plotted
figsize = [12, 6]   # figure size, inches

# network state date from logs or metrics
data = animation_data[0]

matrices = get_matrices(data, objectives)

fig, ax = plt.subplots(nrows=1, ncols=max(objectives + 2, 2), figsize=figsize)
for i, axi in enumerate(ax.flat):
    plot_data = matrices.get(i)
    if plot_data != None:
        (title, min, max, matrix) = plot_data
        axi.set_title(title)
        axi.imshow(matrix, cmap='jet', vmin=min, vmax=max, interpolation='nearest')

plt.tight_layout(True)
plt.show()
