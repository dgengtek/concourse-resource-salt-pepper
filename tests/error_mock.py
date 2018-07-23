import urllib


def build_raise_http_error(url, code):
    http_error = urllib.error.HTTPError(url, code, None, None, None)

    def error(*args, **kwargs):
        raise http_error

    return error
