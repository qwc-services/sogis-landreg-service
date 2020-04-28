from flask import Flask, Response, abort, request, stream_with_context, jsonify
from flask_restplus import Api, Resource
from sqlalchemy.sql import text as sql_text
import requests
import urllib.parse as urlparse
from xml.dom.minidom import parseString

from qwc_services_core.app import app_nocache
from qwc_services_core.auth import auth_manager, optional_auth, get_auth_user
from qwc_services_core.database import DatabaseEngine
from qwc_services_core.tenant_handler import TenantHandler
from qwc_services_core.runtime_config import RuntimeConfig


# Flask application
app = Flask(__name__)
app_nocache(app)
api = Api(app, version='1.0', title='LandRegisterExtract service API',
          description="""API for SO!MAP LandRegisterExtract service.

Delivers a land register extract report.
          """,
          default_label='Land Register Extract operations', doc='/api/')
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

# disable verbose 404 error message
app.config['ERROR_404_HELP'] = False

auth = auth_manager(app, api)

tenant_handler = TenantHandler(app.logger)


# routes
@api.route('/templates')
class LandRegisterTemplates(Resource):

    @api.doc('landregistertemplates')
    @optional_auth
    def get(self):
        """Get available land register templates"""

        tenant = tenant_handler.tenant()
        config_handler = RuntimeConfig("landreg", app.logger)
        config = config_handler.tenant_config(tenant)

        qgis_server_url = config.get('qgis_server_url')
        default_landreg_layout = config.get('default_landreg_layout')
        project = config.get('landreg_project')

        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetProjectSettings",
        }

        url = qgis_server_url.rstrip("/") + "/" + project
        req = requests.get(url, params=params)

        layouts = []
        try:
            capabilities = parseString(req.text)
            templates = capabilities.getElementsByTagName("WMS_Capabilities")[0]\
                                    .getElementsByTagName("Capability")[0]\
                                    .getElementsByTagName("ComposerTemplates")[0]
            for template in templates.getElementsByTagName("ComposerTemplate"):
                name = template.getAttribute("name")
                composerMap = template.getElementsByTagName("ComposerMap")[0]
                entry = {
                    "name": name,
                    "map": {
                        "width": float(composerMap.getAttribute("width")),
                        "height": float(composerMap.getAttribute("height")),
                        "name": composerMap.getAttribute("name")
                    },
                    "default": name == default_landreg_layout
                }
                layouts.append(entry)
        except:
            pass
        return jsonify(layouts)


@api.route('/print')
class LandRegisterExtract(Resource):

    @api.doc('landregisterextract')
    @api.param('TEMPLATE', 'The print template')
    @api.param('EXTENT', 'The extent for the specified map')
    @api.param('SCALE', 'The scale for the specified map')
    @api.param('ROTATION', 'The rotation for the specified map')
    @api.param('DPI', 'The print dpi')
    @api.param('SRS', 'The SRS of the specified map extent')
    @api.param('GRID_INTERVAL_X', 'X grid interval')
    @api.param('GRID_INTERVAL_Y', 'Y grid interval')
    @optional_auth
    def post(self):
        """Submit query

        Return map print
        """
        post_params = dict(urlparse.parse_qsl(request.get_data().decode('utf-8')))
        app.logger.info("POST params: %s" % post_params)

        tenant = tenant_handler.tenant()
        config_handler = RuntimeConfig("landreg", app.logger)
        config = config_handler.tenant_config(tenant)

        db = db_engine.db_engine(config.get('db_url'))
        qgis_server_url = config.get('qgis_server_url')
        project = config.get('landreg_project')
        landreg_printinfo_table = config.get('landreg_printinfo_table')
        landreg_print_layers = config.get('landreg_print_layers')

        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetPrint",
            "FORMAT": "PDF"
        }
        params.update(post_params)

        # Normalize parameter keys to upper case
        params = {k.upper(): v for k, v in params.items()}

        # Set LAYERS and OPACITIES
        params["LAYERS"] = landreg_print_layers
        params["OPACITIES"] = ",".join( map(lambda item: "255", params["LAYERS"].split(",")))

        # Determine center of extent
        extent = list(map(lambda x: float(x), params["EXTENT"].split(",")))
        x = 0.5 * (extent[0] + extent[2])
        y = 0.5 * (extent[1] + extent[3])

        # Determine lieferdatum and nfgeometer
        conn = db.connect()
        sql = sql_text("""
            SELECT nfgeometer, lieferdatum, anschrift, kontakt, gemeinde
            FROM {table}
            WHERE ST_CONTAINS(geometrie, ST_SetSRID(ST_MakePoint(:x, :y), 2056));
        """.format(table=landreg_printinfo_table))

        sql_result = conn.execute(sql, x=x, y=y).fetchone()

        if sql_result:
            params["NFGEOMETER"] = sql_result["nfgeometer"]
            params["LIEFERDATUM"] = sql_result["lieferdatum"]
            params["ANSCHRIFT"] = sql_result["anschrift"]
            params["KONTAKT"] = sql_result["kontakt"]
            params["GEMEINDE"] = sql_result["gemeinde"]

        conn.close()

        # Prefix params with composer map name: Extent, scale, rotation
        params["map0:EXTENT"] = params["EXTENT"]
        del params["EXTENT"]
        params["map0:SCALE"] = params["SCALE"]
        del params["SCALE"]
        params["map0:ROTATION"] = params["ROTATION"]
        del params["ROTATION"]
        if "GRID_INTERVAL_X" in params:
            params["map0:GRID_INTERVAL_X"] = params["GRID_INTERVAL_X"]
            del params["GRID_INTERVAL_X"]
        if "GRID_INTERVAL_Y" in params:
            params["map0:GRID_INTERVAL_Y"] = params["GRID_INTERVAL_Y"]
            del params["GRID_INTERVAL_Y"]

        # Forward to QGIS server
        url = qgis_server_url.rstrip("/") + "/" + project
        req = requests.post(url, timeout=120, data=params)
        app.logger.info("Forwarding request to %s\n%s" % (req.url, params))

        response = Response(
            stream_with_context(
                req.iter_content(chunk_size=1024)
            ), status=req.status_code
        )
        response.headers['content-type'] = req.headers['content-type']
        if req.headers['content-type'] == 'application/pdf':
            response.headers['content-disposition'] = \
                'attachment; filename=' + project + '.' + params['FORMAT'].lower()

        return response


# local webserver
if __name__ == '__main__':
    from flask_cors import CORS
    CORS(app)
    app.run(host='localhost', port=5020, debug=True)
