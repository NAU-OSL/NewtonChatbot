import json
import sys
import os

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado


class ConfigRouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        restrict = []
        instances = False
        for arg in sys.argv:
            lower = arg.lower()
            if lower.startswith('--newtonchat.restrict='):
                restrict = arg[len('--newtonchat.restrict='):].strip('"').strip("'").split(',')
            if lower.startswith('--newtonchat.instances='):
                instances = True
                os.environ["NewtonInstancesPath"] = os.path.join(
                    os.getcwd(),
                    arg[len('--newtonchat.instances='):].strip('"').strip("'")
                )
        self.finish(json.dumps({
            'restrict': restrict,
            'instances': instances,
        }))


class ErrorRouteHandler(APIHandler):
    """Error reported by client. Do nothing for now"""

    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            'status': 'ok'
        }))

    @tornado.web.authenticated
    def post(self):
        self.finish(json.dumps({
            'status': 'ok'
        }))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    config_route_pattern = url_path_join(base_url, "newtonchat", "config")
    error_route_pattern = url_path_join(base_url, "newtonchat", "error")
    handlers = [
        (config_route_pattern, ConfigRouteHandler),
        (error_route_pattern, ErrorRouteHandler)
    ]
    web_app.add_handlers(host_pattern, handlers)
