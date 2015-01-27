from __future__ import print_function

from glue.core import Data
from glue.core.coordinates import coordinates_from_header
from glue.config import data_factory
from glue.core.data_factories import has_extension
from glue.external.astro import fits
import numpy as np

@data_factory('GALFA HI cube', has_extension('fits fit'))
def _load_GALFAHI_data(filename, **kwargs):
    def _get_cube_center(header, cubeshape):
        ra  = header['CRVAL1'] + header['CDELT1'] * (np.arange(cubeshape[2])+0.5 - header['CRPIX1'])              ## degree
        dec = header['CRVAL2'] + header['CDELT2'] * (np.arange(cubeshape[1])+0.5 - header['CRPIX2'])            ## degree
        return np.mean(ra), np.mean(dec)

    # add the primary components
    cube = fits.getdata(filename)
    header = fits.getheader(filename)
    header['CDELT3'] = header['CDELT3'] * (10**(-3))        # m/s --> km/s
    cen_ra, cen_dec = _get_cube_center(header, cube.shape)
    nn = filename.split('/')[-1]
    # cube_name = '%s_RA%dDEC%d' % (nn[0:3], cen_ra, cen_dec)
    cube_name = 'G_%d%+.2fradec_%.1fkm/s_%.1fa' % (cen_ra, cen_dec, header['CDELT3'], header['CDELT2']*60.)

    data = Data()
    data.coords = coordinates_from_header(header)
    data.add_component(cube, cube_name)
    data.label  = cube_name

    data_list = []
    data_list.append(data)
    data_list.append(data)
    return data_list

@data_factory('GALFA HI cube:LowRes', has_extension('fits fit'))
def _load_GALFAHI_data_LowRes(filename, **kwargs):
    # Data loader customized for GALFA-HI data cube
    # Resize the data cube into lower resolution in velocity/space

    def _bin_cube(cube, factor, axis_label):
        # resize the cube to lower resolution
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
        else: new_header = header
        # m/s --> km/s
        new_header['CDELT3'] = new_header['CDELT3'] * (10**(-3))
        return new_header

    def _get_cube_center(header, cubeshape):
        ra  = header['CRVAL1'] + header['CDELT1'] * (np.arange(cubeshape[2])+0.5 - header['CRPIX1'])              ## degree
        dec = header['CRVAL2'] + header['CDELT2'] * (np.arange(cubeshape[1])+0.5 - header['CRPIX2'])            ## degree
        return np.mean(ra), np.mean(dec)

    data_list = []
    # add 3 data objects with different resolutions:
    for factor, axis_label in zip([4, 16, 2], ['VELO', 'VELO', 'RADEC']):
        cube = fits.getdata(filename)
        header = fits.getheader(filename)
        cen_ra, cen_dec = _get_cube_center(header, cube.shape)
        new_header = _get_new_header(header, factor, axis_label)
        cube_name = 'G_%d%+.2fradec_%.1fkm/s_%.1fa' % (cen_ra, cen_dec, new_header['CDELT3'], new_header['CDELT2']*60.)

        data = Data()
        data.coords = coordinates_from_header(new_header)
        data.add_component(_bin_cube(cube, factor, axis_label), cube_name)
        data.label  = cube_name
        data_list.append(data)
        del data, cube, header
    return data_list
