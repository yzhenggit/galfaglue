from __future__ import print_function

import numpy as np
import glue
from scipy.ndimage.morphology import binary_dilation
from glue.core.exceptions import IncompatibleAttribute


def onoff(dc, attribute, roi, spectrum_name="spectrum"):

    # Extract data
    data = dc[attribute]

    # Get limits from ROI
    l, r = np.clip([roi.xmin, roi.xmax], 0, data.shape[2])
    b, t = np.clip([roi.ymin, roi.ymax], 0, data.shape[1])

    # make the 2d on spectrum mask
    mslice = np.zeros(data.shape[1:], dtype=bool)
    mslice[b:t+1,l:r+1] = True

    # make an off spectrum mask
    in_edge_pix = 4
    coreslice = binary_dilation(mslice, iterations=in_edge_pix)
    annular_width_pix = 4
    annslice = binary_dilation(coreslice, iterations=annular_width_pix)
    annslice = annslice-coreslice

    onoffspect = np.zeros(data.shape[0])

    for i, slc in enumerate(data):
        onoffspect[i] = (np.mean(slc[mslice]) -np.mean(slc[annslice]))

    # There is currently a bug that causes cubes to sometimes - but not always
    # have named coordinates.
    try:
        velocity = dc["Velocity", :,0,0]
    except IncompatibleAttribute:
        velocity = dc["World 0", :,0,0]

    return velocity, onoffspect
