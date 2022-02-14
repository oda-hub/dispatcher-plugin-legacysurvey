import requests
import json
import logging

import pytest

logger = logging.getLogger(__name__)

params = {}
params['photometry'] = dict( query_status = "new",
                             query_type = "Real",
                             instrument = "legacysurvey",
                             product_type = "legacy_survey_photometry",
                             T1 = "2017-03-06T13:26:48.000",
                             T2 = "2017-03-06T15:32:27.000",
                             data_release = 9,
                             radius_photometry = 1.0,
                             RA = 166.113808,
                             DEC = 38.208833)

params['image'] = dict( query_status = "new",
                        query_type = "Real",
                        instrument = "legacysurvey",
                        product_type = "legacy_survey_image",
                        T1 = "2017-03-06T13:26:48.000",
                        T2 = "2017-03-06T15:32:27.000",
                        data_release = 9,
                        pixel_size = 1.0,
                        image_size = 3.0,
                        image_band = "g",
                        RA = 166.113808,
                        DEC = 38.208833)

def test_discover_plugin():
    import cdci_data_analysis.plugins.importer as importer

    assert 'dispatcher_plugin_legacysurvey' in  importer.cdci_plugins_dict.keys()

def test_legacysurvey(dispatcher_live_fixture, httpserver, product):
    server = dispatcher_live_fixture
    with open(f'tests/mock_backend_json/Legacysurvey_tap.json', 'r') as fd:
        respjson = json.loads(fd.read())
    httpserver.expect_ordered_request('/').respond_with_data('')    
    httpserver.expect_ordered_request(f'/api/v1.0/get/Legacysurvey_tap').respond_with_json(respjson)
    
    logger.info("constructed server: %s", server)

    c = requests.get(server + "/run_analysis",
                    params = params[product])

    logger.info("content: %s", c.text)
    jdata = c.json()
    logger.info(json.dumps(jdata, indent=4, sort_keys=True))
    logger.info(jdata)
    assert c.status_code == 200

    assert jdata['job_status'] == 'done'
    
    d = requests.get(server + "/download_products",
                    params = {
                        'session_id': jdata['job_monitor']['session_id'],
                        'download_file_name': jdata['products']['download_file_name'],
                        'file_list': jdata['products']['file_name'],
                        'query_status': 'ready',
                        'job_id': jdata['job_monitor']['job_id'],
                        'instrument': 'legacysurvey'
                    })
    assert d.status_code == 200
    