from glue.core import Data, DataCollection
from glue.core.coordinates import coordinates_from_header
from glue.config import data_factory
from glue.core.data_factories import has_extension
from glue.external.astro import fits
import numpy as np

@data_factory('GALFA HI datacube', has_extension('fits'))
def _load_GALFAHI_data(filename, **kwargs):
    # Data loader customized for GALFA-HI data cube

    def _bin_cube(cube, factor, axis_label):
        """
        resize the cube to lower resolution
        """
        shape = cube.shape
        if axis_label == 'VELO':
            new_shape = (shape[0]/factor, factor, shape[1], shape[2])
            return cube.reshape(new_shape).mean(axis = 1)
        elif axis_label == 'RADEC':
            new_shape = (shape[0], shape[1]/factor, factor, shape[2]/factor, factor)
            return cube.reshape(new_shape).mean(axis = 4).mean(axis = 2)
        else: return cube

    # change the header for those cubes that has been binned into low resolutions
    def _get_new_header(header, factor, axis_label):
 	new_header = header
	if axis_label == 'VELO': 
 	    new_header['NAXIS3'] = header['NAXIS3'] / factor
	    new_header['CRVAL3'] = header['CRVAL3']
 	    new_header['CRPIX3'] = float(header['CRPIX3'] / factor)
	    new_header['CDELT3'] = header['CDELT3'] * factor
	elif axis_label == 'RADEC':
	    for ax in [1, 2]: 
	    	new_header['NAXIS%d'%(ax)] = header['NAXIS%d'%(ax)] / factor
                new_header['CRVAL%d'%(ax)] = header['CRVAL%d'%(ax)]
                new_header['CRPIX%d'%(ax)] = float(header['CRPIX%d'%(ax)] / factor)
                new_header['CDELT%d'%(ax)] = header['CDELT%d'%(ax)] * factor
	       
	else: 
	    new_header = header 

	## m/s --> km/s
	new_header['CDELT3'] = new_header['CDELT3'] * (10**(-3))	    
	return new_header


    # add the primary data set with original resolution
    cube = fits.getdata(filename)

    # add 4 data objects with different resolutions:
    # 0-FULL: (2048, 512, 512)
    # 4-VELO: (512, 512, 512)
    # 16-VELO: (126, 512, 512)
    # 2-RADEC: (2048, 256, 256)
    data_list = []
    for factor, axis_label in zip([0, 4, 16, 2], ['FULL', 'VELO', 'VELO', 'RADEC']):
        data = Data()
	header = fits.getheader(filename)
	new_header = _get_new_header(header, factor, axis_label)
	cube_name = 'Cube_%.2f_km/s_%.2f_arcmin' % (new_header['CDELT3'], new_header['CDELT2']*60.)
        data.coords = coordinates_from_header(new_header)
        data.add_component(_bin_cube(cube, factor, axis_label), cube_name)
	data.label  = cube_name	
        data_list.append(data)

    return data_list

