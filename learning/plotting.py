import matplotlib.pyplot as plt
import seaborn as sns
import math
import numpy as np

plt.rc("font", size=14)
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)


def plot_model_scores(scores):
    # number of variable
    categories = scores.columns
    N = len(categories)

    # What will be the angle of each axis in the plot?
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    ax = plt.subplot(111, polar=True)

    # If you want the first axis to be on top:
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories)

    # compute appropriate labels and sizing.
    ymin = np.floor(10 * scores.min().min()) / 10.0
    ymax = np.ceil(10 * scores.max().max()) / 10.0
    yticks = np.round(np.arange(ymin, ymax, 0.05), 2)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks(yticks, [str(val) for val in yticks], color="grey", size=8)
    plt.ylim(ymin, ymax)

    # Plot each individual = each line of the data
    for idx, row in scores.iterrows():
        values = row.values.flatten().tolist()
        values += values[:1]  # start = end for line.
        ax.plot(angles, values, linewidth=1, linestyle="solid", label=idx)

    lgd = ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.1))

    # Show the graph
    plt.savefig(
        "outputs/radarplot.svg",
        bbox_extra_artists=(lgd,),
        bbox_inches='tight'
    )
