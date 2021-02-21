"""Add an example blueprint for odata endpoint"""
import flask

import odata.exc

from odata.helpers.flask.error_handlers import register_error_handlers
from odata.helpers.flask.request import get_parser_kwargs_for_request

blueprint = flask.Blueprint(__name__, __name__)


def add_route_for_odata_parser(routable_flask_obj: Union[flask.App, flask.Blueprint],
                               request_parser: odata.parser.RequestParser):
    @routable_flask_obj.route('/<path:odata_path>')
    def route(odata_path):
        kwargs = get_parser_kwargs_for_request()
        response = request_parser.parse(path=odata_path, **kwargs)
        return flask.jsonify(
                    dict(d=response['payload']),
                    status=response['status'],
                    headers=response['headers']
                )

register_error_handlers(blueprint)
