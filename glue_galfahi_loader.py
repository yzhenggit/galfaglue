from glue.core import Data, DataCollection
from glue.core.coordinates import coordinates_from_header
from glue.config import data_factory
from glue.core.data_factories import has_extension
from glue.external.astro import fits
import numpy as np

@data_factory('GALFA HI datacube', has_extension('fits'))
def _load_GALFAHI_data(filename, **kwargs):
    # Data loader customized for GALFA-HI data cube

    # add the primary data set with original resolution
    cube = fits.getdata(filename)
    header = fits.getheader(filename)
    resolution = [header['CDELT3']*(10**(-3)),    # velocity resolution, km/s
                  header['CDELT2']*60,            # DEC resolution, arcmin 
                  header['CDELT1']*60]            # RA resolution, arcmin


    # primary data, original resolution, (2048, 512, 512)
    data1 = Data()
    data1.coords = coordinates_from_header(header)
    data1.add_component(cube, 'Cube_FullResolution')


    def _bin_cube(cube, factor, axis_label):
        """
        resize the cube to lower resolution
        """
        shape = cube.shape
        if axis_label == 'Velocity':
            new_shape = (shape[0]/factor, factor, shape[1], shape[2])
            return cube.reshape(new_shape).mean(axis = 1)
        if axis_label == 'RADEC':
            new_shape = (shape[0], shape[1]/factor, factor, shape[2]/factor, factor)
            return cube.reshape(new_shape).mean(axis = 4).mean(axis = 2)
        else: return cube


    # lower the velocity resolution --> (512, 512, 512)
    data2 = Data()
    cube_name = 'Cube_VelRes_%.2f_kms' % (resolution[0] * 4)
    data2.coords = coordinates_from_header(header)
    data2.add_component(_bin_cube(cube, 4, 'Velocity'), cube_name)

    # lower the velocity resolution --> (128, 512, 512) 
    data3 = Data()
    cube_name = 'Cube_VelRes_%.2f_kms' % (resolution[0] * 16)
    data3.coords = coordinates_from_header(header)
    data3.add_component(_bin_cube(cube, 16, 'Velocity'), cube_name)

    # lower the spatial resolution --> (2048, 256, 256)
    data4 = Data()
    cube_name = 'Cube_SpaRes_%.2f_arcmin' % (resolution[1] * 2)
    data4.coords = coordinates_from_header(header)
    data4.add_component(_bin_cube(cube, 2, 'RADEC'), cube_name)

    return [data1, data2, data3, data4]

