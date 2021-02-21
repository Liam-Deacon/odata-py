"""Helper for flask requests within odata"""
from typing import Any, Dict

from flask import request


def get_parser_kwargs_for_request() -> Dict[str, Any]:
    """Create default kwargs for `odata.RequestParser.parse()` from `flask.request` information"""
    return dict(
        http_verb=flask.request.method,
        headers=flask.request.headers,
        query_args=flask.request.args,
        payload=flask.request.form
                if flask.request.form
                else flask.request.data
    )
