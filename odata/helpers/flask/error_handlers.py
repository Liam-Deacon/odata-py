"""Provides convenience functions for flask error handling"""
import flask 

import odata.exc


def default_request_parse_error_func(err):
    return flask.jsonify({'error': err.message}, 400)


def default_not_implemented_error_func(err):
    return flask.jsonify({'error': 'Feature not yet implemented'}, 400)


def default_no_content_func(err):
    return flask.Response(status=err.code)


def register_error_handlers(
        routable_flask_obj: Union[flask.App, flask.Blueprint],
        request_parse_error_func=default_request_parse_error_func,
        not_implemented_error_func=default_not_implemented_error_func,
        no_content_func=default_no_content_func
    ):
    """Register error handlers to `flask_obj`, using defaults when no functions specified"""
    request_parse_error_func = request_parse_error_func
    not_implemented_error_func = not_implemented_error_func
    no_content_func = no_content_func

    if request_parse_error_func:
        routable_flask_obj.errorhandler(odata.exc.RequestParseError)(request_parse_error_func)
    if not_implemented_error_func:
        routable_flask_obj.errorhandler(NotImplementedError)(not_implemented_error_func)
    if no_content_func:
        routable_flask_obj.errorhandler(odata.exc.NoContent)(no_content_func)
