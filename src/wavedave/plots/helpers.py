def sync_yscales(axes):
    """Synchronizes the y-axis of a list of axes"""

    # get the limits
    limits = [ax.get_ylim() for ax in axes]
    # get the min and max
    min_ = min([l[0] for l in limits])
    max_ = max([l[1] for l in limits])
    # set the limits
    for ax in axes:
        ax.set_ylim(min_, max_)

    return axes

def apply_default_style(fig, axes):

    fig.set_facecolor('white')
    fig.tight_layout()

    # set font
    for ax in axes:
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(8)
            item.set_fontname('Arial')

    for ax in axes:
        ax.set_facecolor('white')

        # dashed grid
        ax.grid(linestyle='--', linewidth = 0.5)


    return fig