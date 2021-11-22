from cdci_data_analysis.analysis.products import QueryOutput
from cdci_data_analysis.configurer import DataServerConf
import requests
import time

class LegacySurveyDispatcher:
    def __init__(self, instrument=None, param_dict=None, task=None, config=None):
        if config is None:
            config = DataServerConf.from_conf_dict(instrument.data_server_conf_dict)
        self.data_server_url = config.data_server_url
        self.task = task
        self.param_dict = param_dict

    def test_communication(self, max_trial=10, sleep_s=1, logger=None):
        print('--> start test connection')

        query_out = QueryOutput()
        no_connection = True
        excep = Exception()
        
        print('url', self.data_server_url)
        url = self.data_server_url

        for i in range(max_trial):
            try:
                res = requests.get("%s" % (url), params=None)
                print('status_code',res.status_code)
                if res.status_code !=200:
                    no_connection =True
                    raise ConnectionError(f"Backend connection failed: {res.status_code}")
                else:
                    no_connection=False

                    message = 'Connection OK'
                    query_out.set_done(message=message, debug_message='OK')
                    print('-> test connections passed')
                    break
            except Exception as e:
                excep = e
                no_connection = True

            time.sleep(sleep_s)

        if no_connection is True:
            query_out.set_query_exception(excep, 
                                          'no data server connection',
                                          logger=logger)
            raise ConnectionError('Backend connection failed')

        return query_out
    

    def test_has_input_products(self, instrument, logger=None):
        print('--> test for data availability')
        print('dummy OK')
        query_out = QueryOutput()
        query_out.set_done('data available')
        return query_out, [1]
    

    def run_query(self,
                  call_back_url=None,
                  run_asynch = False,
                  logger=None,
                  task = None,
                  param_dict=None):
        
        res = None
        message = ''
        debug_message = ''
        query_out = QueryOutput()

        if task is None:
            task=self.task     

        if param_dict is None:
            param_dict=self.param_dict   

        #TODO: handle fail
        url = "%s/%s" % (self.data_server_url, task)
        res = requests.get("%s" % (url), params = param_dict)
        query_out.set_done(message=message, debug_message=str(debug_message),job_status='done')

        return res, query_out