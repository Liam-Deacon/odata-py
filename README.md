# Python implementation of the ODATA version 4 standard using SQLAlchemy

This package aims to support ODATA version 4 standard using SQLAlchemy - it is very much a work in progress, so PRs (or any other contributions) would be greatly appreciated!

When a feature is described in the odata documentation but not yet implemented in code a `NotImplementedError` will be raised.
The code has only had limited testing, but sqlalchmy expression builder has been used extensivly in the hope that the code will be made portable for targeting multiple SQL DBMSs.

## Example

Full examples can be found under the [examples/](https://github.com/Liam-Deacon/odata-py/tree/master/examples) directory.

A minimal example of how to plug the `odata` package into your existing SQLAlchemy database table models would be:

```python
import flask
import sqlalchemy
import odata

from odata.helpers.flask.error_handlers import register_error_handlers
from odata.helpers.flask.request import get_parser_kwargs_for_request

# db
engine = sqlalchemy.create_engine('sqlite://my-database.db')  # change this to your own (preexisting) database and specify engine options to suit

# create a RequestParser instance this will handle the odata path, headers, query args parsing
request_parser = odata.parser.RequestParser(engine=engine)  # optionally provide tables and dialect kwargs

# Flask related setup
app = flask.Flask(__name__)

# register error hanlders to app
register_error_handlers(app)

# Try hitting localhost:5000/demo.svc/<table>?$top=3
@app.route('/demo.svc/<path:odata_path>')
def route(odata_path):
    kwargs = get_parser_kwargs_for_request()
    response = request_parser.parse(path=odata_path, **kwargs)
    return flask.jsonify(dict(d=response['payload']),
                         status=response['status'],
                         headers=response['headers'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

```

## Development Setup

Simply install this package using pip (ideally in a virtualenv):

```bash
python -m pip install -e .  # where the current working directory is the repo root
```

## Specification Documentation

- [ODATA v4.01 Protocol](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html)
- [ODATA v4.01 URL Conventions](https://docs.oasis-open.org/odata/odata/v4.01/os/part2-url-conventions/odata-v4.01-os-part2-url-conventions.html)

# TODO

The following are areas of activities to be done:

- [ ] Implement minimum ODATA v4 standard (including `$metadata`)
- [ ] Create a CI/CD pipeline
    - [ ] Linting and static analysis
    - [ ] Code Coverage checks
    - [ ] Deploy odata package to PyPI
- [ ] Create documentation
    - [ ] Setup sphinx tooling
    - [ ] Add documentation task(s) to CI pipeline
    - [ ] Push documentation to readthedocs.org or github pages
- [ ] Add some Shields.io badges!

## Acknkowledgements

This repo is based off the [original odata-py work](https://github.com/jisaacstone/odata-py) by [jisaacstone](https://github.com/jisaacstone) targeting ODATA v3. 
