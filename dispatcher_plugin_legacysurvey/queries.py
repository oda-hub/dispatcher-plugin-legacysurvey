import numpy as np
from cdci_data_analysis.analysis.queries import BaseQuery, ProductQuery
from cdci_data_analysis.analysis.parameters import Integer, ParameterTuple, Name, Angle
from cdci_data_analysis.analysis.products import QueryOutput, BaseQueryProduct
from oda_api.data_products import ODAAstropyTable, NumpyDataProduct, NumpyDataUnit 
from astropy.io import ascii
from astropy.io import fits
import os
from cdci_data_analysis.analysis.catalog import BasicCatalog
from .products import LSPhotometryProduct


class LSInstrumentQuery(BaseQuery):
    def __init__(self, 
                 name):
        data_release = Integer(value=9, name='data_release')
        param_list = [data_release]
        self.input_prod_list_name = None
        super().__init__(name, param_list)

class LSPhotometryQuery(ProductQuery):
    def __init__(self, name):
                radius_photometry = Angle(value=3, units='arcsec', default_units='arcsec', name='radius_photometry')
                parameters_list = [radius_photometry]
                super().__init__(name, parameters_list)

    def get_data_server_query(self, instrument, config, **kwargs):
        param_dict = dict(ra_s = instrument.get_par_by_name('RA').value,
                          dec_s = instrument.get_par_by_name('DEC').value,
                          radius_photometry = instrument.get_par_by_name('radius_photometry').value,
                          dr = instrument.get_par_by_name('data_release').value)
        return instrument.data_server_query_class(instrument=instrument,
                                                  config=config,
                                                  param_dict=param_dict,
                                                  task='/api/v1.0/get/Legacysurvey_tap')

    def build_product_list(self, instrument, res, out_dir, api=False):
        prod_list = []
        if out_dir is None:
            out_dir = './'
        _o_dict = res.json()
        spec = ascii.read(_o_dict['output']['spec'])
        
        photometry = LSPhotometryProduct(spec, 
                                     'desi_legacysurvey_photometry', 
                                     'desi_legacysurvey_photometry.fits',
                                     out_dir = out_dir,
                                     )
        prod_list.append(photometry)       
        return prod_list

    def process_product_method(self, instrument, prod_list, api=False):
        if api is True:
            raise NotImplementedError
        else:
            prod  = prod_list.prod_list[0]
            html_dict = prod.get_plot()
            prod.write()
            
            plot_dict = {}
            plot_dict['image'] = html_dict
            plot_dict['header_text'] = ''
            plot_dict['table_text'] = ''
            plot_dict['footer_text'] = ''
            
            query_out = QueryOutput()
            query_out.prod_dictionary['name'] = 'photometry'
            query_out.prod_dictionary['file_name'] = str(prod.file_path.name)
            query_out.prod_dictionary['image'] = plot_dict
            query_out.prod_dictionary['download_file_name'] = 'legacysurvey_photometry.fits.gz'
            query_out.prod_dictionary['prod_process_message'] = ''

        return query_out
    
class LSImageProduct:
    def __init__(self, header_str, data, image = None, out_dir = None):
        self.header = fits.Header.fromstring(header_str)
        self.data = np.array(data)
        self.image = image
        self.out_dir = out_dir
        
    def write(self):
        hdu = fits.PrimaryHDU(self.data)
        hdu.header = self.header
        hdul = fits.HDUList([hdu])
        hdul.writeto(self.out_dir + '/legacysurvey_image.fits', overwrite=True)
                
    def get_plot(self):
        script = ''
        div = f'<img width=800 src="data:image/jpeg;base64,{self.image}">'
        return script, div            

class LSCatalog(BasicCatalog):
    pass

        
class LSImageQuery(ProductQuery):
    def __init__(self, name):
                image_band = Name(value='g', name='image_band')
                image_size = Angle(value=3., units='arcmin', default_units='arcmin', name='image_size')
                pixel_size = Angle(value=1., units='arcsec', default_units='arcsec', name='pixel_size')
                parameters_list = [image_band, image_size, pixel_size]
                super().__init__(name, parameters_list)

    def get_data_server_query(self, instrument, config, **kwargs):
        param_dict = dict(ra_s = instrument.get_par_by_name('RA').value,
                          dec_s = instrument.get_par_by_name('DEC').value,
                          dr = instrument.get_par_by_name('data_release').value,
                          image_band = instrument.get_par_by_name('image_band').value,
                          image_size = instrument.get_par_by_name('image_size').value,
                          pixsize = instrument.get_par_by_name('pixel_size').value)

        return instrument.data_server_query_class(instrument=instrument,
                                                  config=config,
                                                  param_dict=param_dict,
                                                  task='/api/v1.0/get/Legacysurvey_tap')

    def build_product_list(self, instrument, res, out_dir, api=False):
        prod_list = []
        if out_dir is None:
            out_dir = './'
        _o_dict = res.json()      
        image_str = _o_dict['output']['image_log']
        imfits_head = _o_dict['output']['imfits_head']
        imfits_data = _o_dict['output']['imfits_data']
        catalog = _o_dict['output']['catalog']
                
        image = LSImageProduct(imfits_head, imfits_data, image_str, out_dir)
        prod_list.append(image)
        #TODO add catalog
        return prod_list

    def process_product_method(self, instrument, prod_list, api=False):
        if api is True:
            raise NotImplementedError
        else:
            prod  = prod_list.prod_list[0]
            script, div = prod.get_plot()
            html_dict = {}
            html_dict['script'] = script
            html_dict['div'] = div
            plot_dict = {}
            plot_dict['image'] = html_dict
            plot_dict['header_text'] = ''
            plot_dict['table_text'] = ''
            plot_dict['footer_text'] = ''

            prod.write()
            query_out = QueryOutput()
            query_out.prod_dictionary['name'] = 'spectrogram'
            query_out.prod_dictionary['file_name'] = 'legacysurvey_image.fits'
            query_out.prod_dictionary['image'] = plot_dict
            query_out.prod_dictionary['download_file_name'] = 'legacysurvey_image.fits'
            query_out.prod_dictionary['prod_process_message'] = ''

        return query_out
        
