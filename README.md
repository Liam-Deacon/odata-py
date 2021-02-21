# Python implementation of the ODATA version 4 standard using SQLAlchemy

This package aims to support ODATA version 4 standard using SQLAlchemy - it is very much a work in progress, so PRs (or any other contributions) would be greatly appreciated!

When a feature is described in the odata documentation but not yet implemented in code a `NotImplementedError` will be raised.
The code has only had limited testing, but sqlalchmy expression builder has been used extensivly in the hope that the code will be made portable for targeting multiple SQL DBMSs.

## Specification Documentation

- [ODATA v4.01 Protocol](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part1-protocol.html)
- [ODATA v4.01 URL Conventions](https://docs.oasis-open.org/odata/odata/v4.01/os/part2-url-conventions/odata-v4.01-os-part2-url-conventions.html)

## Acknkowledgements

This repo is based off the [original odata-py work](https://github.com/jisaacstone/odata-py) by [jisaacstone](https://github.com/jisaacstone) targeting ODATA v3. 
