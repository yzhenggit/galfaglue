### 
# 20141204, initial script provided by Chris Beaumont 
# 20141204, modified by Yong Zheng

from glue import custom_viewer, qglue
from glue.core.data_factories import load_data
import numpy as np
from glue.clients.ds9norm import DS9Normalize
from glue.core.subset import RoiSubsetState
from glue.core.util import color2rgb
import pyfits

global ra, dec, vlsr, delta_vlsr, region, cube_id

filename = '/Volumes/My Passport/Research/GALFA/t2s3/cubes/GALFA_HI_RA+DEC_316.00+10.35_W.fits'
region = 't2s3'
cube_id = 'GALFA_HI_RA+DEC_316.00+10.35_W'

# load data 
data = load_data(filename)

# read in header to calculate the RA, DEC, VLSR
hd   = pyfits.getheader(filename)
ra   = hd['CRVAL1'] + hd['CDELT1'] * (np.arange(data.shape[0])+1 - hd['CRPIX1'])              ## degree
dec  = hd['CRVAL2'] + hd['CDELT2'] * (np.arange(data.shape[1])+1 - hd['CRPIX2'])            ## degree
vlsr = (hd['CRVAL3'] + hd['CDELT3'] * (np.arange(data.shape[2])+1 - hd['CRPIX3']))*(10**(-3)) ## km/s
delta_vlsr = hd['CDELT3']*(10**(-3))

# define the galfa-hi viewer
galfa_viewer = custom_viewer('GALFA-RGB Viewer',  # name of viewer
                       # velocity=(0, data.shape[0]),   # slider for velocity channel
		       # center = (2, data.shape[0] - 3),
		       center_kms = (-600, 600), # center of velocity in km/s
                       width_kms=(1, 50),    # slider for RGB channel offset, in km/s
                       data='att',       # dropdown to choose data attribute to image
	               Mean= False | True, 
                       redraw_on_settings_change = True  # rerender data if settings change
                       )



@galfa_viewer.plot_data
def draw(axes, data, center_kms, width_kms, Mean):	
    import numpy as np
    """
    Make a 3 color image showing a cube slice (g),
    slice - width (r), slice + width (b)
    """
    if data is None or data.size == 0 or data.ndim != 3:
        return

    width_pixel = int(width_kms/delta_vlsr)
    hw_pixel = np.ceil(width_pixel/2.)

    # extract rgb slices
    center_pixel = (center_kms-vlsr.min())/delta_vlsr

    cen_g  = center_pixel
    g = data[max(cen_g - hw_pixel, 0):min(cen_g + hw_pixel, data.shape[0]-1), :, :]

    cen_r  = center_pixel -hw_pixel
    r = data[max(cen_r - hw_pixel, 0):min(cen_r + hw_pixel, data.shape[0]-1), :, :]

    cen_b = center_pixel + hw_pixel
    b = data[max(cen_b - hw_pixel, 0):min(cen_b + hw_pixel, data.shape[0]-1), :, :]

    if Mean:
	g = np.mean(g, axis = 0)
	r = np.mean(r, axis = 0)
 	b = np.mean(b, axis = 0)
    else:
	g = np.sum(g, axis = 0)
        r = np.sum(r, axis = 0)
        b = np.sum(b, axis = 0)


    rgb = np.nan_to_num(np.dstack((r, g, b)))

    # manually rescale intensities from 0-1
    norm = DS9Normalize()
    norm.vmin = -0.2
    norm.vmax = 10.
    # adjusting the min-max of the image
    # dump = data[np.logical_not(np.isnan(data))]
    # if dump.min() < 0: norm.vmin = dump.min() * (Color_MinMax/100.)
    # else: norm.vmin = dump.min() / (Color_MinMax/100.)
    # norm.vmax = dump.max() * Color_MinMax/100.
    norm.stretch = 'arcsinh'
    # norm.stretch = 'linear'
    rgb = norm(rgb)
    
    axes.imshow(rgb, origin='lower', extent = [ra.max(), ra.min(), dec.min(), dec.max()], aspect = 3.5)
    axes.set_xlabel('RA')
    axes.set_ylabel('DEC')
    axes.set_title('%s/%s' % (region, cube_id))


@galfa_viewer.plot_subset
def draw_subset(axes, subset, center_kms, style):
    """
    Draw a subset as a semi-transparent box
    """
    # get the RGB color of the subset
    r, g, b = color2rgb(style.color)

    # extract a True/False array of mask, at the center slice
    center_pixel = (center_kms - vlsr.min())/delta_vlsr
    m = subset.to_mask((center_kms,))

    # turn into a RGBA array
    m = np.dstack((r * m, g * m, b * m, m * 0.7))
    m = (255 * m).astype(np.uint8)

    # draw it
    axes.imshow(m, alpha=0.5, origin='lower', interpolation='nearest')


@galfa_viewer.make_selector
def make_selector(roi):
    # turn a selection into a subset
    # XXX this is brittle, since it relies on the names 'Pixel X'
    # and 'Pixel y' for the pixel coordinates. This will probably
    # cause problems related to name ambiguities if several cubes
    # are loaded into Glue
    return RoiSubsetState(xatt='Pixel x', yatt='Pixel y', roi=roi)

qglue(data=data)
