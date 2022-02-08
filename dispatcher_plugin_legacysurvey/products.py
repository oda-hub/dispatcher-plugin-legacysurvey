from oda_api.data_products import ODAAstropyTable
from cdci_data_analysis.analysis.products import BaseQueryProduct
from cdci_data_analysis.analysis.plot_tools import ScatterPlot

from bokeh.plotting import figure
from bokeh.models import ColorBar, LinearColorMapper, HoverTool, CustomJS, Slider 
from bokeh.embed import components
from bokeh.layouts import row, widgetbox, column

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