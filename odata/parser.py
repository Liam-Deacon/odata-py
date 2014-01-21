from sqlalchemy.sql import expression
from sqlalchemy import select, insert, update, delete
from sqlalchemy.dialects.oracle import dialect as OracleDialect

from odata import urlpath, urlquery, urlheaders
from odata.exc import RequestParseError, NoContent
from odata.shared import select_star


verbfuncs = dict(
    GET=lambda table: select().select_from(table),
    POST=insert,
    PUT=update,
    PATCH=update,
    MERGE=update,
    DELETE=delete)


def create_context(tables, http_verb, headers=None, payload=None):
    if http_verb not in verbfuncs:
        raise RequestParseError('Unknown verb')
    return dict(
        tables=tables,
        http_verb=http_verb,
        request_payload=payload,
        request_headers=headers if headers is not None else {},
        sqlobj=verbfuncs[http_verb],
        response_headers={},
        response_status=200)


def validate_and_cleanup(sqlobj, request_payload):
    if isinstance(sqlobj, expression.Select):
        if not sqlobj.columns:
            return select_star(sqlobj)

    if ((isinstance(sqlobj, expression.Update) or
            isinstance(sqlobj, expression.Delete)) and
            not sqlobj._whereclause):
        raise RequestParseError('Global collection modifications not allowed')

    if ((isinstance(sqlobj, expression.Update) or
            isinstance(sqlobj, expression.Insert)) and
            not sqlobj.parameters):
        if hasattr(request_payload, 'iteritems'):
            return sqlobj.values(request_payload)
        else:
            raise RequestParseError('Invalid Payload')

    return sqlobj


class RequestParser(object):
    def __init__(self, tables, dialect=None, query_func=None):
        if dialect is None:
            dialect = OracleDialect()
        self.dialect = dialect
        self.tables = tables
        self.query_func = query_func

    def parse(self, path, http_verb,
              headers=None, query_args=None, payload=None):
        context = create_context(self.tables, http_verb, headers, payload)
        urlpath.parse(path, context)
        if query_args:
            urlquery.parse(context, query_args)
        if headers:
            urlheaders.parse(context)
        context['sqlobj'] = validate_and_cleanup(context['sqlobj'], payload)
        response = self.query(context)
        return dict(payload=response,
                    headers=context['response_headers'],
                    status=context['response_status'])

    def query(self, context):
        query, binds = self.compile(context['sqlobj'])
        try:
            response = self.query_func(query, binds)
        except NoContent as e:
            e.code = context['response_status']
            raise e
        return response

    def compile(self, sqlobj):
        complied = sqlobj.compile(dialect=self.dialect)
        print unicode(complied), complied.params
        return unicode(complied), complied.params
