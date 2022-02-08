from .dataserver_dispatcher import LegacySurveyDispatcher
from cdci_data_analysis.analysis.instrument import Instrument
from .queries import LSInstrumentQuery, LSPhotometryQuery, LSImageQuery
from cdci_data_analysis.analysis.queries import SourceQuery
from . import conf_file

def legacysurvey_factory():
    src_query = SourceQuery('src_query')
    instr_query = LSInstrumentQuery('instr_query')
    ls_spec_query = LSPhotometryQuery('ls_photometry_query')
    ls_image_query = LSImageQuery('ls_image_query')

    query_dictionary = {}
    query_dictionary['legacy_survey_photometry'] = 'ls_photometry_query'
    query_dictionary['legacy_survey_image'] = 'ls_image_query'

    return Instrument('legacysurvey', 
                      src_query=src_query,
                      instrumet_query=instr_query,
                      data_serve_conf_file=conf_file,
                      asynch=False, 
                      product_queries_list=[ls_spec_query, ls_image_query],
                      data_server_query_class=LegacySurveyDispatcher,
                      query_dictionary=query_dictionary)