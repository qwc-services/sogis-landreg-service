SO!GIS Land Register Extract service
====================================

Delivers a land register extract report.


Configuration
-------------

A QGIS Project containing layers and print templates to use for the land
register extract (Grundbuchauszug) must be placed in the `qgs-resources/`
docker volume. Project name and layers must be specified using the config
outlined below.

The static config files are stored as JSON files in `$CONFIG_PATH` with subdirectories for each tenant,
e.g. `$CONFIG_PATH/default/*.json`. The default tenant name is `default`.

### MapInfo Service config

* [JSON schema](schemas/sogis-landreg-service.json)
* File location: `$CONFIG_PATH/<tenant>/mapinfoConfig.json`

Example:
```json
{
  "$schema": "https://raw.githubusercontent.com/qwc-services/sogis-landreg-service/master/schemas/sogis-landreg-service.json",
  "service": "landreg",
  "config": {
    "db_url": "postgresql:///?service=qwc_geodb",
    "qgis_server_url": "http://qwc-qgis-server/ows",
    "landreg_project": "landreg",
    "landreg_print_layers": "parcels",
    "landreg_printinfo_table": "qwc_geodb.print_info",
    "default_landreg_layout": "A4-Portrait"
  }
}
```

### Environment variables

Config options in the config file can be overridden by equivalent uppercase environment variables.

| Variable                  | Description                                     |
|---------------------------|-------------------------------------------------|
| `QGIS_SERVER_URL`         | QGIS Server URL                                 |
| `LANDREG_PROJECT`         | QGIS project name                               |
| `LANDREG_PRINT_LAYERS`    | Layer names to print                            |
| `LANDREG_PRINTINFO_TABLE` | Table containing `nfgeometer` and `lieferdatum` |
| `DEFAULT_LANDREG_LAYOUT`  | Default print template for land register extract|


Usage
-----

Run as

    python server.py

API documentation:

    http://localhost:5020/api/

Development
-----------

Create a virtual environment:

    python3 -m venv .venv

Activate virtual environment:

    source .venv/bin/activate

Install requirements:

    pip install -r requirements.txt

Start local service:

    CONFIG_PATH=/PATH/TO/CONFIGS/ python server.py


Testing
-------

Run all tests:

    python test.py

