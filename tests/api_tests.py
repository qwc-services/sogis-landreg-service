import os
import unittest
from urllib.parse import urlparse, parse_qs, unquote_plus

from flask import Response, json
from flask.testing import FlaskClient
from flask_jwt_extended import JWTManager, create_access_token

import server


class ApiTestCase(unittest.TestCase):
    """Test case for server API"""

    def setUp(self):
        os.environ["LANDREG_PROJECT"] = "test_grundbuch"
        os.environ["LANDREG_PRINT_LAYERS"] = "test_layer"
        os.environ["LANDREG_PRINTINFO_TABLE"] = "test.print_info"

        server.app.testing = True
        self.app = FlaskClient(server.app, Response)
        JWTManager(server.app)

    def tearDown(self):
        pass

    def jwtHeader(self):
        with server.app.test_request_context():
            access_token = create_access_token('test')
        return {'Authorization': 'Bearer {}'.format(access_token)}

    def test_templates(self):
        response = self.app.get('/templates', headers=self.jwtHeader())
        self.assertEqual(200, response.status_code, "Status code is not OK")

    def test_print(self):
        params = {
            'TEMPLATE': 'A4_portrait',
            'DPI': 300,
            'SRS': 'EPSG:2056',
            'EXTENT': '2605354,1227225,2608612,1229926',
            'SCALE': 1000,
            'ROTATION': 0,
            'GRID_INTERVAL_X': 1000,
            'GRID_INTERVAL_Y': 1000
        }
        expect_params = {
            'TEMPLATE': 'A4_portrait',
            'DPI': 300,
            'SRS': 'EPSG:2056',
            'map0:EXTENT': '2605354,1227225,2608612,1229926',
            'map0:SCALE': 1000,
            'map0:ROTATION': 0,
            'map0:GRID_INTERVAL_X': 1000,
            'map0:GRID_INTERVAL_Y': 1000,
            'NFGEOMETER': "Dominik Cantaluppi",
            'LIEFERDATUM': "2018-04-12",
            'ANSCHRIFT': "Emch+Berger AG Vermessungen, Schöngrünstrasse 35, 4500 Solothurn",
            'KONTAKT': "Tel.: 032 624 48 48, Fax: 032 624 48 96, E-Mail: vermessung@emchberger.ch, Web: www.vermessung.emchberger.ch",
            'GEMEINDE': "Gemeinde Solothurn"
        }
        response = self.app.post('/print', data=params, headers=self.jwtHeader())
        self.assertEqual(200, response.status_code, "Status code is not OK")
        data = json.loads(response.data)
        self.assertEqual('test_grundbuch', data['path'], 'Print project name mismatch')
        self.assertEqual('POST', data['method'], 'Method mismatch')
        print_params = dict([list(map(unquote_plus, param.split("=", 1))) for param in data['data'].split("&")])
        for param in expect_params.keys():
            self.assertTrue(param in print_params, "Parameter %s missing in response" % param)
            self.assertEqual(print_params[param], str(expect_params[param]), "Parameter %s mismatch" % param)
