import numpy as np
import matplotlib.pyplot as plt
from extract import get_matrices

objectives = 3      # amount of objectives to be plotted
figsize = [12, 6]   # figure size, inches

# network state date from logs or metrics
# NOTE data is truncated
data = (-13,2,-7,4,5,[(-10,2,0.0463873,12,[0.0330982,2.3859062,1377.8985269,613.3774599,214.4931558],[[0.0000000,99.0000000,60088.0252449],[0.0000000,99.0000000,60338.6566134],]),(-11,-2,0.0615927,158,[0.0257947,2.1717231,1391.2495835,617.6731287,215.1266496],[[0.0000000,97.0000000,62541.9058931],[0.0000000,97.0000000,63129.3991759],])])

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
