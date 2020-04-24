Land Register Extract service
=============================

Delivers a land register extract report.


Dependencies
------------

* QGIS Server


Configuration
-------------

A QGIS Project containing layers and print templates to use for the land
register extract (Grundbuchauszug) must be placed in the `qgs-resources/`
docker volume. Project name and layers must be specified using the environment
variables listed below.

Environment variables:

| Variable                  | Description                                     |
|---------------------------|-------------------------------------------------|
| `QGIS_SERVER_URL`         | QGIS Server URL                                 |
| `LANDREG_PROJECT`         | QGIS project name                               |
| `LANDREG_PRINT_LAYERS`    | Layer names to print                            |
| `LANDREG_PRINTINFO_TABLE` | Table containing `nfgeometer` and `lieferdatum` |
| `DEFAULT_LANDREG_LAYOUT`  | Default print template for land register extract|


Usage
-----

API documentation:

    http://localhost:5020/api/


Development
-----------

Create a virtual environment:

    virtualenv --python=/usr/bin/python3 .venv

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

