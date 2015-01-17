class PyAggError(Exception):
    status_code = None
    default_message = ''


class Forbidden(PyAggError):
    status_code = 403
    default_message = 'You do not have the rights to access that resource'


class NotFound(PyAggError):
    status_code = 404
    default_message = 'Resource was not found'
