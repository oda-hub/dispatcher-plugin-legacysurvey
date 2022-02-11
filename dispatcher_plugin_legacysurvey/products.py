from oda_api.data_products import ODAAstropyTable, NumpyDataUnit, NumpyDataProduct
from cdci_data_analysis.analysis.products import BaseQueryProduct, ImageProduct, CatalogProduct
from cdci_data_analysis.analysis.plot_tools import ScatterPlot
from astropy.io import ascii
import numpy as np

class LSPhotometryProduct(BaseQueryProduct):
    def __init__(self, spec_table, name, file_name, out_dir = None, prod_prefix = None, meta_data = {}):
        self.file_name = file_name
        
        super().__init__(name=name,
                         file_name = file_name,
                         file_dir = out_dir,
                         name_prefix=prod_prefix,
                         data = None,
                         meta_data = meta_data)
        
        self.data = ODAAstropyTable(spec_table, name=name, meta_data = meta_data)
        
    def get_plot(self):
        w, h = 600, 400
        data = self.data.table
        
        e_range = data['E']
        points = data['nuFnu']
        errors = data['nuFnu_err']
        
        if len(data) > 0:
            sp = ScatterPlot(w = w, h = h, 
                             x_label = str(e_range.unit),
                             y_label = str(points.unit),
                             y_axis_type = 'log',
                             x_axis_type = 'log')
            sp.add_errorbar(e_range, points, yerr=errors)
        else:
            sp = ScatterPlot(w = w, h = h, 
                             x_label = 'eV',
                             y_label = '',
                             y_axis_type = 'log',
                             x_axis_type = 'log')
             
        return  sp.get_html_draw()
    
class LSImageProduct(ImageProduct):
    def __init__(self, header, data, name='legacysurvey_image', file_name='legacysurvey_image.fits', out_dir = None, meta_data={}):
        data = np.array(data)
        data_unit = NumpyDataUnit(data, header, hdu_type='image', name='image')
        data_prod = NumpyDataProduct(data_unit, name=name)
        super().__init__(name, data_prod, file_name, meta_data, file_dir = out_dir)

#TODO: it would be better to refactor BasicCatalog to be more universal and use it
class LSCatalog: 
    def __init__(self, atable):
        self._table = atable
        self.columns_to_show = ['ra', 'dec', #'mjd_min', 'mjd_max', 
                                'flux_g', #'flux_ivar_g',
                                'flux_r', #'flux_ivar_r',
                                'flux_z', #'flux_ivar_z',
                                'flux_w1', #'flux_ivar_w1',
                                'flux_w2', #'flux_ivar_w2',
                                'flux_w3', #'flux_ivar_w3',
                                'flux_w4', #'flux_ivar_w4',
                                ]
        self._table_reduced = self._table[self.columns_to_show]
        
    @property
    def table(self):
        return self._table

    @property
    def name(self):
        return np.array(['']*len(self.table), dtype='object')
    
    @property
    def ra(self):
        return self.table['ra'].value
    
    @property
    def dec(self):
        return self.table['dec'].value
    
    @classmethod
    def from_encoded_table(cls, enc_table):
        atable = ascii.read(enc_table)
        return cls(atable)
    
    def add_column(self, name, values, index=None):
        self.table.add_column(values, name=name, index=index)
    
    def write(self, name, format='fits', overwrite=True):
        self._table.write(name, format=format, overwrite=overwrite)        
    
    def get_dictionary(self, api=False):
        if api:
            table = self._table
        else:
            table = self._table_reduced
        
        table.add_column(np.arange(len(table)), name='index', index=0)
        
        column_lists=[table[name].tolist() for name in table.colnames]
        
        for ID,_col in enumerate(column_lists):
            column_lists[ID] = [x if str(x)!='nan' and str(x)!='inf' else None for x in _col]
            
        catalog_dict = dict(cat_column_list=column_lists,
                cat_column_names=table.colnames,
                cat_column_descr=table.dtype.descr,
                cat_meta = table.meta
                )
        return catalog_dict                    
    
class LSCatalogProduct(CatalogProduct):
    pass