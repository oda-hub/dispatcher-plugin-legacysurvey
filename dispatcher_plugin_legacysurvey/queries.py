from cdci_data_analysis.analysis.queries import BaseQuery, ProductQuery
from cdci_data_analysis.analysis.parameters import Integer, Name, Angle
from cdci_data_analysis.analysis.products import QueryOutput
from astropy.io import ascii
from .products import LSCatalog, LSPhotometryProduct, LSImageProduct, LSCatalogProduct

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
        query_out = QueryOutput()
        prod  = prod_list.prod_list[0]
        if api is True:
            query_out.prod_dictionary['astropy_table_product_ascii_list'] = [prod.data.encode(use_binary=False)]
        else:
            html_dict = prod.get_plot()
            prod.write()
            
            plot_dict = {}
            plot_dict['image'] = html_dict
            plot_dict['header_text'] = ''
            plot_dict['table_text'] = ''
            plot_dict['footer_text'] = ''
            
            query_out.prod_dictionary['name'] = 'photometry'
            query_out.prod_dictionary['file_name'] = str(prod.file_path.name)
            query_out.prod_dictionary['image'] = plot_dict
            query_out.prod_dictionary['download_file_name'] = 'legacysurvey_photometry.fits.gz'
            query_out.prod_dictionary['prod_process_message'] = ''

        return query_out
    
       
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
        imfits_head = _o_dict['output']['imfits_head']
        imfits_data = _o_dict['output']['imfits_data']
        catalog_str = _o_dict['output']['catalog']
                
        image = LSImageProduct(imfits_head, 
                               imfits_data, 
                               out_dir = out_dir, 
                               name='legacysurvey_image', 
                               file_name='legacysurvey_image.fits')
        prod_list.append(image)
        
        catalog = LSCatalog.from_encoded_table(catalog_str)
        cat_prod = LSCatalogProduct('legacysurvey_catalog', 
                                    catalog, 
                                    file_dir = out_dir, 
                                    file_name='catalog')
        prod_list.append(cat_prod)
        
        return prod_list

    def process_product_method(self, instrument, prod_list, api=False):
        query_out = QueryOutput()
        image_prod  = prod_list.get_prod_by_name('legacysurvey_image')
        catalog_prod = prod_list.get_prod_by_name('legacysurvey_catalog')

        if api is True:
            query_out.prod_dictionary['numpy_data_product_list'] = [ image_prod.data ]
            query_out.prod_dictionary['catalog'] = catalog_prod.catalog.get_dictionary(api=True)
        else:
            plot_dict = image_prod.get_html_draw(catalog_prod.catalog)
            image_prod.write()
            catalog_prod.write(format='fits')

            query_out.prod_dictionary['name'] = image_prod.name
            query_out.prod_dictionary['file_name'] = [str(image_prod.file_path.name), 
                                                      str(catalog_prod.file_path.name)+'.fits']
            query_out.prod_dictionary['image'] = plot_dict
            query_out.prod_dictionary['download_file_name'] = 'legacysurvey_image.tar.gz'
            query_out.prod_dictionary['prod_process_message'] = ''
            query_out.prod_dictionary['catalog'] = catalog_prod.catalog.get_dictionary(api=False)

        return query_out
        
