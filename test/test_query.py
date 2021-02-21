from itertools import product
from sqlalchemy import select
from fixtures import users, addresses
from odata import urlquery
from odata.exc import RequestParseError

import pytest


def context(sqlobj):
    return dict(
        sqlobj=sqlobj,
        headers={})

def S():
    return select().select_from(users)


@pytest.mark.parametrize('context,qargs,expected', [
    (context(S()),
     {'$select': 'id'},
     str(S().column(users.c.id))),
    (context(S()),
     {'$select': '*'},
     str(users.select())),
    (context(S()),
     {'$select': 'users.id'},
     str(S().column(users.c.id))),
    (context(S()),
     {'$select': 'users.*'},
     str(users.select())),
    (context(select().select_from(users.join(addresses))),
     {'$select': 'name'},
     str(select([users.c.name]).select_from(users.join(addresses)))),
    (context(S()),
     {'$select': 'name,fullname'},
     str(select([users.c.name, users.c.fullname], None, [users]))),
    (context(S()),
     {'$top': '5'},
     str(S().limit(5))),
    (context(S()),
     {'$skip': '5'},
     str(S().offset(5))),
    ])
def test(context, qargs, expected):
    try:
        ctx = urlquery.parse(context, qargs)
    except NotImplementedError:
        pytest.skip("not implemented")
    else:
        assert str(ctx['sqlobj']) == expected


qargs = ['$select', '$top', '$skip', '$filter']
vals = ['badstringvalue', None, '']
bad_inputs = ((context(S()), {q: v}) for q, v in product(qargs, vals))


@pytest.mark.parametrize('context,qargs', bad_inputs)
def test_matrix_fail(context, qargs):
    with pytest.raises(RequestParseError):
        urlquery.parse(context, qargs)


@pytest.mark.parametrize('context,qargs', [
    (context(users.join(addresses).select()), {'$select': 'id'}),
    (context(users.update()), {'$select': 'name'}),
    ])
def test_req_parse_error(context, qargs):
    with pytest.raises(RequestParseError):
        urlquery.parse(context, qargs)
