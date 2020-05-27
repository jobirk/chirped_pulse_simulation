import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib import animation
# import scipy.constants as con
from IPython.display import HTML
from tqdm import tqdm
# import matplotlib.cm as cm

c = 1


def k(nu, nu_center, k0=1, k1=0, k2=0):
    """Calculates the wave vector k as a function of the frequency nu 

    Parameters
    ----------
    k0 : float, optional
        Zero-order derivative 
    k1 : float, optional
        First order derivative dk/dω
    k2 : float, optional
        Second order derivative d^2k/dω^2

    Returns
    -------
    k : float
        Wave vector k(ω)

    """

    omega = 2 * np.pi * nu
    omega_0 = 2 * np.pi * nu_center

    return k0 + k1 * (omega - omega_0) + k2 * (omega - omega_0)**2


def sin_sum(z, t, nu_center=1, nu_min=0.001, N_frequencies=4000, spec_width=200, 
            k_i=[1, 5, 0], plotting=False, z_arrow=False, figuresize=(11, 4)):
    """Calculates the sum of plane waves (sinusoidal signals) over a
       given frequency spectrum 

    Parameters
    ----------
    z : array_like
        Array of the z-axis your wave packet is propagating on.
    t : float
        Time at which you want to calculate the current spatial form of the 
        wave (snapshot along the z-axis at that point in time).
    nu_center : float, optional
        Center frequency of the frequency spectrum you are using in the 
        simulation. Default is 1.
    nu_min : float, optional
        Minimal frequency that is included in the spectrum. By default the 
        spectrum from nu_min to 2*nu_center is considered. Therefore, if you
        are using a very low nu_center, you may have to adjust nu_min as well.
        Default is 0.001.
    N_frequencies : int, optional
        Number of frequencies (spectral components) included in the sum. The
        final spectrum is a numpy.linspace(nu_min, 2 * nu_center). The default
        value for N_frequencies is 4000.
    spec_width : int, optional
        Width of the spectrum. The spectrum is a gaussian signal obtained from 
        scipy. The variable spec_width is not exactly the spectral width Δν.
        Instead, a gaussian along the range (0, N_frequencies) is generated
        with standard deviation spec_width. So if you want e.g. a very sharp
        peak at nu_center with N_frequencies=4000, choose e.g. spec_width=100.
        Default is 100.
    k_i : list of floats, optional
        List that contains the values you want to use for the 
        frequency-dependent wave vector k. Default is [1, 5, 0]. 
    plotting : bool, optional
        Bool to turn on the plotting, which will plot some spectral components,
        the resulting total wave (the wave packet) and the underlying spectrum.
        Default is False.
    z_arrow : bool, optional
        Option to plot a arrow with the label 'position z' along the direction
        of propagation. Default is False.
    figuresize : tuple of ints, optional
        Size of the figure when plotting the wave. Default is (11, 4).

    Returns
    -------
    E : array
        E-field amplitude along the z-axis at time t.

    """  

    # create array of frequency spectrum and the corresponding weight 
    # i.e. how much the given frequency contributes
    frequencies = np.linspace(nu_min, nu_center * 2, N_frequencies)
    spectrum = signal.gaussian(len(frequencies), std=spec_width)

    # create array for spectral components
    E_nu = np.zeros([len(frequencies), len(z)])

    n_plotted = 0
    N_spec_plot_tot = 20
    N_spec_plot_min = int(2 * N_frequencies/5)
    N_spec_plot_max = int(3*N_frequencies/5)
    spacing = int(len(frequencies[N_spec_plot_min:N_spec_plot_max]) / N_spec_plot_tot)
    plotting_frequencies = frequencies[N_spec_plot_min: N_spec_plot_max: spacing]
    # colors = cm.rainbow(np.linspace(0, 1, N_spec_plot_tot))

    if plotting:
        fig, ax = plt.subplots(figsize=figuresize, frameon=False)
        ax.set_xlim(z.min(), z.max())
        plt.axis('off')

    # now loop over all frequencies and calculate the corresponding spectral
    # component
    for i in range(len(frequencies)):
        phi_nu = k(frequencies[i], nu_center, *k_i) * z
        E_nu[i, :] = spectrum[i] * np.sin(2 * np.pi * frequencies[i] * t - phi_nu)

        if plotting:
            if frequencies[i] in plotting_frequencies:
                ax.plot(z, E_nu[i], label=frequencies[i])  # , color=colors[n_plotted])
                n_plotted += 1

    E = E_nu.sum(axis=0)

    # plot the different spectral components (in the center of the spectrum),
    # the resulting pulse (sum of the spectral components) and the underlying
    # spectrum
    if plotting:
        ymin = E_nu.min() * 1.1
        ymax = E_nu.max() * 1.1
        ax.set_ylim(ymin, ymax)
        print("plotted", n_plotted, "frequencies")
        plt.show()
        fig.savefig("plots/spectral_components.pdf")

        # now plot the resulting pulse
        fig, ax = plt.subplots(figsize=figuresize, frameon=False)
        ax.set_xlim(z.min(), z.max())
        plt.axis('off')
        ymin = E.min() * 2
        ymax = E.max()
        ax.set_ylim(ymin, ymax)
        ax.plot(z, E)
        fig.savefig("plots/resulting_pulse.pdf")

        # also plot the spectrum
        fig, ax = plt.subplots(figsize=(6, 4), frameon=False)
        ax.plot(frequencies, spectrum)
        ax.set_xlabel(r"Frequency $\nu$")
        ax.set_ylabel(r"Spectral amplitude $S(\nu)$")
        fig.savefig("plots/spectrum.pdf")

    return E


def calc_pulses(z, t_start, t_end, n_steps, nu_center=1, k_i=[1, 5, 0],
                spec_width=100):
    """Calculates the spatial form of the pulse at different times 

    Parameters
    ----------
    z : array_like
        Array of the z-axis your wave packet is propagating on.
    t_start : float
        Start time of the propagation.
    t_end : float
        End time of the propagation.
    n_steps : int
        Number of time steps you want to animate.
    nu_center : float, optional
        Center frequency of the frequency spectrum you are using in the 
        simulation. Default is 1.
    k_i : list of floats, optional
        List that contains the values you want to use for the 
        frequency-dependent wave vector k. Default is [1, 5, 0]. 
    spec_width : int, optional
        Width of the spectrum. The spectrum is a gaussian signal obtained from 
        scipy. The variable spec_width is not exactly the spectral width Δν.
        Instead, a gaussian along the range (0, N_frequencies) is generated
        with standard deviation spec_width. So if you want e.g. a very sharp
        peak at nu_center with N_frequencies=4000, choose e.g. spec_width=100.
        Default is 100.

    Returns
    -------
    pulses : array
        Array of shape (n_steps, len(z)), which contains the electric field of
        the wave at all time steps.

    """

    times = np.linspace(t_start, t_end, n_steps)
    pulses = np.zeros([n_steps, len(z)])
    for i in tqdm(range(len(times))):
        pulses[i, :] = sin_sum(z, times[i], nu_center=nu_center, k_i=k_i,
                               spec_width=spec_width)

    return pulses


def animate(z, pulses, ms_between_frames=30, figuresize=(11, 4)):
    """Animates the time evolution of the wave packet 

    Parameters
    ----------
    z : array_like
        Array of the z-axis your wave packet is propagating on.
    pulses : array
        Array of shape (n_steps, len(z)), which contains the electric field of
        the wave at all time steps.
    ms_between_frames : int, optional
        Milliseconds of pause between two frames in the animation. Default 
        is 30.
    figuresize : tuple of ints, optional
        Size of the figure when plotting the wave. Default is (11, 4).

    """

    fig, ax = plt.subplots(figsize=figuresize)

    ax.set_xlim(z.min(), z.max())
    ax.set_ylim(1.2 * pulses.min(), 1.2 * pulses.max())

    ax.set_xlabel(r"position $z$")

    lines = [ax.plot([], [], color="forestgreen")[0]
             for i in pulses]

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def animate(i):
        for j in range(len(lines)):
            lines[j].set_data(z, pulses[i, :])
        return lines

    plt.close()
    anim = animation.FuncAnimation(fig, animate, init_func=init, blit=True,
                                   frames=len(pulses), 
                                   interval=ms_between_frames)
    # Writer = animation.writers['ffmpeg']
    # writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    # anim.save("animation.mp4", writer=writer)
    return HTML(anim.to_html5_video())


def plot_pulses(z, times, nu_center=0.5, k_i=[1, 10, 0], spec_width=400, 
                no_axes=False, plotname="", dpi=100, figuresize=(11, 4), 
                z_arrow=False, colors=["steelblue" for i in range(10)]):
    """Plots the pulse at different times 

    Parameters
    ----------
    z : array_like
        Array of the z-axis your wave packet is propagating on.
    times : array_like
        Array of the points in time you want to plot.
    nu_center : float, optional
        Center frequency of the frequency spectrum you are using in the 
        simulation. Default is 1.
    k_i : list of floats, optional
        List that contains the values you want to use for the 
        frequency-dependent wave vector k. Default is [1, 5, 0]. 
    spec_width : int, optional
        Width of the spectrum. The spectrum is a gaussian signal obtained from 
        scipy. The variable spec_width is not exactly the spectral width Δν.
        Instead, a gaussian along the range (0, N_frequencies) is generated
        with standard deviation spec_width. So if you want e.g. a very sharp
        peak at nu_center with N_frequencies=4000, choose e.g. spec_width=100.
        Default is 100.
    no_axes : bool, optional
        Option to turn of the plotting of the axes. Default is False.
    plotname : str, optional
        Path of the plot, except for the ".pdf", in case you want to save the 
        plot. If more than one time step is to be plotted, the for each time 
        step a plot is produced, containing the previous timesteps and the 
        current one. Default is "", corresponding to not saving the plot.
    dpi : int, optional
        Number of DPI in the plots. Default is 100.
    figuresize : tuple of ints, optional
        Size of the figure when plotting the wave. Default is (11, 4).
    z_arrow : bool, optional
        Option to plot a arrow with the label 'position z' along the direction
        of propagation. Default is False.
    colors : list of str, optional
        The colors you want to use for the different time steps. By default all
        time steps are plotted with the standard python 'steelblue'.

    """

    pulses = [sin_sum(z, t, nu_center=nu_center, k_i=k_i, spec_width=spec_width) for t in times]

    fig, ax = plt.subplots(figsize=figuresize, dpi=dpi, frameon=False)

    ax.set_xlim(z.min(), z.max())
    ymax = pulses[0].max() * 1.1
    ymin = pulses[0].min() * 1.1
    if z_arrow:
        ymin *= 2
    ax.set_ylim(ymin, ymax)

    if no_axes:
        # remove axes and draw arrow in z-direction
        plt.axis('off')
        if z_arrow:
            arrow_coord = (z.mean() - 0.2 * z.mean(), z.mean() + 0.2 * z.mean(), 
                           ymin, ymin)
            text_coord  = [z.mean() - 0.1 * z.mean(), z.mean(), 
                           0.9 * ymin, 0.9 * ymin]
            ax.annotate("", xytext=(arrow_coord[0], arrow_coord[2]), 
                        xy=(arrow_coord[1], arrow_coord[3]),
                        arrowprops=dict(arrowstyle='->'))
            ax.annotate("position $z$", xytext=(text_coord[0], text_coord[2]), 
                        xy=(text_coord[1], text_coord[3]))
    for i in range(len(pulses)):
        ax.plot(z, pulses[i], color=colors[i])
        if plotname != "":
            if len(pulses) > 1:
                fig.savefig(plotname+"_"+str(i+1)+".pdf")
            else:
                fig.savefig(plotname+".pdf")
    plt.show()


