from glue import custom_viewer, qglue
from glue.clients.ds9norm import DS9Normalize

import numpy as np
import pyfits

# define the galfa-hi viewer
galfa_rgb_viewer = custom_viewer('GALFA-RGB Viewer',  # name of viewer
                   center_kms = (-600, 600),          # center of velocity in km/s
                   width_kms=(1, 50),                 # width of RGB channel in km/s
                   data='att',                        # dropdown to choose data attribute to image
                   redraw_on_settings_change = True   # rerender data if settings change
                  )


@galfa_viewer.plot_data
def draw(axes, data, ra, dec, vlsr, center_kms, width_kms):
    """
    Make a 3 color image showing a cube slice (g), slice - width (r), slice + width (b)
    data: 3D numpy arrays
    ra, dec, vlsr: 1D array, showing the grid points on each of the axis
    """
    if data is None or data.size == 0 or data.ndim != 3:
        return

    delta_vlsr = vlsr[1] - vlsr[0]
    width_pixel = int(width_kms/delta_vlsr)

    hw_pixel = np.ceil(width_pixel/2.)

    # extract rgb sub_cubes with some velocity width
    center_pixel = (center_kms-vlsr.min())/delta_vlsr

    cen_g  = center_pixel
    g = data[max(cen_g - hw_pixel, 0):min(cen_g + hw_pixel, data.shape[0]-1), :, :]

    cen_r  = center_pixel -hw_pixel
    r = data[max(cen_r - hw_pixel, 0):min(cen_r + hw_pixel, data.shape[0]-1), :, :]

    cen_b = center_pixel + hw_pixel
    b = data[max(cen_b - hw_pixel, 0):min(cen_b + hw_pixel, data.shape[0]-1), :, :]

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
    axes.imshow(rgb, origin='lower', extent = [ra.max(), ra.min(), dec.min(), dec.max()], aspect = 1.)
    axes.set_xlabel('RA')
    axes.set_ylabel('DEC')

