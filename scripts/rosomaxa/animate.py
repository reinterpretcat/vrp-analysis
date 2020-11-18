import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from extract import get_matrices
from data import animation_data


objectives = 3      # amount of objectives to be plotted
weights = 5         # amount of weights
figsize = [12, 8]   # figure size, inches
plotsize = [2, 6]   # amout of subplots in plot


class AnimationPlayer():
    def __init__(self, fig, ani):
        self.pause = False
        self.ani = ani
        fig.canvas.mpl_connect('button_press_event', self.onClick)

    def onClick(self, event):
        if self.pause:
            self.ani.event_source.stop()
        else:
            self.ani.event_source.start()
        self.pause ^= True


# determine grid size
rows_min = sys.maxsize
rows_max = -sys.maxsize
cols_min = sys.maxsize
cols_max = -sys.maxsize
for data in animation_data:
    (data_rows_min, data_rows_max, data_cols_min, data_cols_max, _, _) = data
    rows_min = min(rows_min, data_rows_min)
    rows_max = max(rows_max, data_rows_max)
    cols_min = min(cols_min, data_cols_min)
    cols_max = max(cols_max, data_cols_max)

animation_matrices = []
for data in animation_data:
    matrices = get_matrices(data, objectives, weights, rows_min,
                            rows_max, cols_min, cols_max)
    animation_matrices.append(matrices)


fig, ax = plt.subplots(nrows=plotsize[0], ncols=plotsize[1], figsize=figsize)

ims = []
for i in range(0, len(animation_matrices)):
    ims_frame = []
    for j, axi in enumerate(ax.flat):
        plot_data = animation_matrices[i].get(j)
        if plot_data != None:
            (title, min, max, matrix) = plot_data
            axi.set_title(title)
            min = min - (max - min) * 0.1
            im = axi.imshow(matrix, cmap='gist_earth', vmin=min, vmax=max)
            ims_frame.append(im)
        else:
            axi.set_visible(False)

    ims.append(ims_frame)

ani = animation.ArtistAnimation(
    fig, ims, interval=1000, blit=True, repeat_delay=1000)
player = AnimationPlayer(fig, ani)

# ani.save('mwe.mp4')

plt.tight_layout(True)
plt.show()
