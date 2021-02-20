"""This module defines exception classes for odata"""

class RequestParseError(Exception):
    """Generic ODATA query parsing error"""
    pass

class NotFoundException(Exception):
    """Exception class for 404 NOT_FOUND error"""
    pass


class NoContent(Exception):
    """Class for declaring No Content is available"""
    def __init__(self, code=204):
        self.code = code
        Exception.__init__(self)
