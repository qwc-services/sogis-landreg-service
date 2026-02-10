SO!GIS Land Register Extract service
====================================

Delivers a land register extract report.

A QGIS Project containing layers and print templates to use for the land
register extract (Grundbuchauszug) must be placed in the `qgs-resources/`
docker volume. Project name and layers must be specified using the config
outlined below.


Configuration
-------------

The static config files are stored as JSON files in `$CONFIG_PATH` with subdirectories for each tenant,
e.g. `$CONFIG_PATH/default/*.json`. The default tenant name is `default`.

### LandReg Service config

* [JSON schema](schemas/sogis-landreg-service.json)
* File location: `$CONFIG_PATH/<tenant>/landregConfig.json`

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

Run locally
-----------

Install dependencies and run:

    export CONFIG_PATH=<CONFIG_PATH>
    uv run src/server.py

To use configs from a `qwc-docker` setup, set `CONFIG_PATH=<...>/qwc-docker/volumes/config`.

Set `FLASK_DEBUG=1` for additional debug output.

Set `FLASK_RUN_PORT=<port>` to change the default port (default: `5000`).

API documentation:

    http://localhost:5000/api/

Docker usage
------------

The Docker image is published on [Dockerhub](https://hub.docker.com/r/sourcepole/sogis-landreg-service).

See sample [docker-compose.yml](https://github.com/qwc-services/qwc-docker/blob/master/docker-compose-example.yml) of [qwc-docker](https://github.com/qwc-services/qwc-docker).

