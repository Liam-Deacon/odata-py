"""Render payload based on Content-Type header"""
from json import JSONEncoder, dumps
from odata.exc import RequestParseError


class ReprEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int,
                            float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        return repr(obj)


def jsonify(payload) -> str:
    """Encode `payload` as JSON string"""
    return dumps(payload, cls=ReprEncoder)


def plaintext(payload) -> str:
    """Encode `payload` as plaintext"""
    if hasattr(payload, 'values'):
        payload = list(payload.values())
    if isinstance(payload, list) or isinstance(payload, tuple):
        if len(payload) != 1:
            raise RequestParseError('No plaintext support for this endpoint')
        payload = payload[0]
    return payload


def xml(payload) -> str:
    """Encode payload to XML string"""
    raise NotImplementedError  # TODO: implement XML translation


def atom_xml(payload) -> str:
    raise NotImplementedError  # TODO: implement XML translation


formatters = {
    'application/json': jsonify,
    'text/plain': plaintext,
    'application/xml': xml,
    'application/xml+atom': atom_xml
}


def payload(context) -> str:
    """Get a payload string based on header Content-Type, defaulting to 'application/json'"""
    headers = context.get('headers', {})
    code = context.get('response_code', 200)
    ct = context.get('content_type',
                     headers.get('Content-Type', 'application/json'))
    try:
        payload = formatters[ct](context.get('payload', ''))
    except (KeyError, NotImplementedError):
        raise NotImplementedError('"Content-Type: {ct}" not implemented'.format(ct=ct))
    return payload
