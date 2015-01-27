from __future__ import print_function

import numpy as np
import glue
from scipy.ndimage.morphology import binary_dilation

def lookup_data_subset(dc, data_name, subset_name):
    data_labels = [d.label for d in dc]
    data = dc[data_labels.index(data_name)]

    subset_labels = [s.label for s in data.subsets]
    subset = data.subsets[subset_labels.index(subset_name)]

    return data, subset

def onoff(dc, data_name, subset_name, spectrum_name="spectrum"):

    # read in the appropriate Data and Subset
    Mydata, Mysubset = lookup_data_subset(dc, data_name, subset_name)

    # make the 2d on spectrum mask
    mslice = Mysubset.to_mask(np.s_[0,:,:])

    # make an off spectrum mask

    in_edge_pix = 4
    coreslice = binary_dilation(mslice, iterations=in_edge_pix)
    annular_width_pix = 4
    annslice = binary_dilation(coreslice, iterations=annular_width_pix)
    annslice = annslice-coreslice

    onoffspect = np.zeros(Mydata.shape[0])

    for i, slc in enumerate(Mydata["PRIMARY"]):
        onoffspect[i] = (np.mean(slc[mslice]) -np.mean(slc[annslice]))

    print(annslice.shape)
    print(onoffspect.shape)

    #for i in xrange(onoffspect.size):
    #       slc=Mydata["PRIMARY", i, :, :]
    #       onoffspect[i] = (np.mean(slc[mslice]) -np.mean(slc[annslice]))


    data = glue.core.Data(Tb=onoffspect, label=spectrum_name)
    velocity_id = Mydata.id['Velocity']
    data.add_component(Mydata["Velocity", :,0,0], label=velocity_id)
    dc.append(data)
