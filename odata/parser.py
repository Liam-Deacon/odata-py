from typing import Any, Dict, List, Optional, Union

import sqlalchemy

from sqlalchemy.sql import expression
from sqlalchemy import select, insert, update, delete

from odata import urlpath, urlquery, urlheaders, render
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
            sqlobj._whereclause is None):
        raise RequestParseError('Global collection modifications not allowed')

    if ((isinstance(sqlobj, expression.Update) or
            isinstance(sqlobj, expression.Insert)) and
            not sqlobj.parameters):
        if hasattr(request_payload, 'items'):
            return sqlobj.values(request_payload)
        else:
            raise RequestParseError('Invalid Payload')

    return sqlobj


class RequestParser:
    """This class parses HTTP queries connecting to SQLAlchemy engine object"""
    def __init__(self,
            tables: Optional[List[str]] = None,
            engine: Optional[sa.engine.Engine] = None,
            dialect: Optional[str] = None,
            connection: Optional[sa.engine.Connection] = None):
        """Create a new request parser object
        
        Parameters
        ----------
        tables
            List of tables to allow queries on (default is to use all tables provided by `engine.table_names()`).
        engine
            The SQLAlchemy engine instance to use. Must be provided when no values are given for
            `connection` and `tables`.
        dialect
            The SQLAlchemy dialect to use (uses `engine.dialect` by default). This is primarily used to govern
            capabilities based on underlying DBMS.
        connection
            The SQLAlchemy connection instance to use for the request.
        
        Raises
        ------
        ValueError
            When neither `tables` nor `engine` is specified.

        """
        self.engine = engine
        self.tables: List[str] = tables
        self.dialect: Optional[str] = dialect or getattr(self.engine, 'dialect', None)
        self.connection = connection

    @property
    def tables(self):
        return self._tables

    @tables.setter
    def tables(self, tables: Optional[List[str]]):
        try:
            self._tables = tables or self.engine.table_names()
        except AttributeError:
            raise ValueError('tables list must be provided when no engine is specified')

    def parse(self, path, http_verb,
              headers=None, query_args=None, payload=None):
        context = create_context(self.tables, http_verb, headers, payload)
        urlpath.parse(path, context)
        if query_args:
            urlquery.parse(context, query_args)
        if headers:
            urlheaders.parse(context)
        context['sqlobj'] = validate_and_cleanup(context['sqlobj'], payload)
        try:
            context['payload'] = self.query(context['sqlobj'])
        except NoContent as e:
            e.code = context['response_status']
            raise e
        return self.render(context)

    def query(self, sqlobj) -> List[Dict[str, Any]]:
        if self.connection is None:
            if self.engine is not None:
                connection = self.engine.connect()
            else:
                raise AttributeError("No connection or engine found")
        else:
            connection = self.connection()
        sqlobj = sqlobj.compile(self.engine, self.dialect)
        result = connection.execute(sqlobj)
        if not result.returns_rows:
            raise NoContent()
        return list(map(dict, result))

    def render(self, context):
        return dict(payload=render.payload(context),
                    headers=context['response_headers'],
                    status=context['response_status'])
