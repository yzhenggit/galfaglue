### 
# 20141204, Chris Beaumont 

from glue import custom_viewer, qglue
from glue.core.data_factories import load_data
import numpy as np
from glue.clients.ds9norm import DS9Normalize
from glue.core.subset import RoiSubsetState
from glue.core.util import color2rgb

# data = load_data('/Volumes/My Passport/Research/GALFA/t2s3/cubes/GALFA_HI_RA+DEC_316.00+10.35_W.fits')

viewer = custom_viewer('GALFA-RGB Viewer',  # name of viewer
                       center=(900, 1100),   # slider for velocity channel
                       width=(1, 50),  # slider for RGB channel offset
                       data='att',       # dropbox to choose data attribute to image
                       redraw_on_settings_change = True  # rerender data if settings change
                       )



@viewer.plot_data
def draw(axes, data, center, width):
    """
    Make a 3 color image showing a cube slice (g),
    slice - width (r), slice + width (b)
    """
    if data is None or data.size == 0 or data.ndim != 3:
        return

    # extract rgb slices
    g = data[center]
    r = data[max(center - width, 0)]
    b = data[min(center + width, data.shape[0] - 1)]
    rgb = np.nan_to_num(np.dstack((r, g, b)))

    # manually rescale intensities from 0-1
    norm = DS9Normalize()
    norm.vmin = 0.1
    norm.vmax = 10.
    norm.stretch = 'arcsinh'
    rgb = norm(rgb)
    axes.imshow(rgb, origin='lower')


@viewer.plot_subset
def draw_subset(axes, subset, center, style):
    """
    Draw a subset as a semi-transparent box
    """
    # get the RGB color of the subset
    r, g, b = color2rgb(style.color)

    # extract a True/False array of mask, at the center slice
    m = subset.to_mask((center,))

    # turn into a RGBA array
    m = np.dstack((r * m, g * m, b * m, m * 0.7))
    m = (255 * m).astype(np.uint8)

    # draw it
    axes.imshow(m, alpha=0.5, origin='lower', interpolation='nearest')


@viewer.make_selector
def make_selector(roi):
    # turn a selection into a subset
    # XXX this is brittle, since it relies on the names 'Pixel X'
    # and 'Pixel y' for the pixel coordinates. This will probably
    # cause problems related to name ambiguities if several cubes
    # are loaded into Glue
    return RoiSubsetState(xatt='Pixel x', yatt='Pixel y', roi=roi)

# qglue(data=data)
qglue()
