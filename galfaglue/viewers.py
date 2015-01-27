from __future__ import print_function

from glue import custom_viewer
from glue.clients.ds9norm import DS9Normalize

import numpy as np

# define the galfa-hi viewer
galfa_rgb_viewer = custom_viewer('GALFA-HI RGB Viewer',  # name of viewer
                   data = 'att',
                   center = (-600, 600),          # center of velocity in km/s
                   width =(1, 50),                 # width of RGB channel in km/s
                   redraw_on_settings_change = True   # rerender data if settings change
                  )


@galfa_rgb_viewer.plot_data
def draw(axes, data, center, width, layer):
    """
    Make a 3 color image showing a data slice (g), slice - width (r), slice + width (b)
    data: 3D numpy arrays
    ra, dec, vlsr: 1D array, showing the grid points on each of the axis
    """
    if data is None or data.size == 0 or data.ndim != 3:
        return

    velocity = layer['Velocity', :, 0, 0]
    dec = layer['Declination', 0, :, 0]
    ra = layer['Right Ascension', 0, 0, :]

    velo_pix = velocity[1] - velocity[0]

    npix_width = int(width/velo_pix)
    npix_hw    = np.ceil(npix_width/2.)

    # extract rgb sub_datas with some velocity width
    cenpix_g  = int((center - velocity.min())/velo_pix)
    g = data[max(cenpix_g - npix_hw, 0):min(cenpix_g + npix_hw, data.shape[0]-1), :, :]

    cenpix_r  = cenpix_g - npix_hw
    r = data[max(cenpix_r - npix_hw, 0):min(cenpix_r + npix_hw, data.shape[0]-1), :, :]

    cenpix_b = cenpix_g + npix_hw
    b = data[max(cenpix_b - npix_hw, 0):min(cenpix_b + npix_hw, data.shape[0]-1), :, :]

    # take the mean for each r, g, b slice
    g = np.mean(g, axis = 0)
    r = np.mean(r, axis = 0)
    b = np.mean(b, axis = 0)


    rgb = np.nan_to_num(np.dstack((r, g, b)))

    # manually rescale intensities from 0-1
    norm = DS9Normalize()
    norm.vmin = -0.2
    norm.vmax = 10.
    norm.stretch = 'arcsinh'

    rgb = norm(rgb)
    axes.imshow(rgb, origin='lower', extent = [ra.max(), ra.min(), dec.min(), dec.max()])
    axes.set_xlabel('RA')
    axes.set_ylabel('DEC')
    # axes.set_title(data.label)
