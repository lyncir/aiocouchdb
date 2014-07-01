# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.
#

import asyncio
from aiohttp.errors import HttpException


class CouchHttpError(BaseException):
    """Mixin class to denote CouchDB related errors."""

    error = ''
    reason = ''

    def __init__(self, error, reason, headers=None):
        self.error = error
        self.reason = reason
        self.headers = headers

    def __str__(self):
        return self.reason


class BadRequest(CouchHttpError, HttpException):
    """The request could not be understood by the server due to malformed
    syntax."""

    code = 400
    message = 'Bad Request'

    def __str__(self):
        if self.error:
            return '({}) {}'.format(self.error, self.reason)
        return super().__str__()


class Unauthorized(CouchHttpError, HttpException):
    """The request requires user authentication."""

    code = 401
    message = 'Unauthorized'


class Forbidden(CouchHttpError, HttpException):
    """The server understood the request, but is refusing to fulfill it."""

    code = 403
    message = 'Forbidden'


class ResourceNotFound(CouchHttpError, HttpException):
    """The server has not found anything matching the Request-URI."""

    code = 404
    message = 'Resource Not Found'


class MethodNotAllowed(CouchHttpError, HttpException):
    """The method specified in the Request-Line is not allowed for
    the resource identified by the Request-URI."""

    code = 405
    message = 'Method Not Allowed'


class ResourceConflict(CouchHttpError, HttpException):
    """The request could not be completed due to a conflict with the current
    state of the resource."""

    code = 409
    message = 'Resource Conflict'


class PreconditionFailed(CouchHttpError, HttpException):
    """The precondition given in one or more of the Request-Header fields
    evaluated to false when it was tested on the server."""

    code = 412
    message = 'Precondition Failed'


class ServerError(CouchHttpError, HttpException):
    """The server encountered an unexpected condition which prevented it from
    fulfilling the request."""

    code = 500
    message = 'Server Error'

    def __str__(self):
        if self.error:
            return '({}) {}'.format(self.error, self.reason)
        return super().__str__()


HTTP_ERROR_BY_CODE = {err.code: err for err in CouchHttpError.__subclasses__()}


@asyncio.coroutine
def maybe_raise_error(resp):
    """Raises :exc:`aiohttp.errors.HttpException` exception in case of >=400
    response status code."""
    if resp.status < 400:
        return
    exc_cls = HTTP_ERROR_BY_CODE[resp.status]
    data = yield from resp.json(close=True)
    if isinstance(data, dict):
        error, reason = data.get('error', ''), data.get('reason', '')
        exc = exc_cls(error, reason, resp.headers)
    else:
        exc = exc_cls('', data, resp.headers)
    raise exc
