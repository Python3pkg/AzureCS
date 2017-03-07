"""
Michael duPont - michael@mdupont.com
"""

# pylint: disable=C0111,C0321

from requests.status_codes import _codes

def exception_factory(name: str, msg: str) -> Exception:
    """Generate an Exception child class with a given name and error message"""
    class New(Exception): pass
    New.__name__ = name
    return New(msg)

def httpcode_exception(code: int, msg: str) -> Exception:
    """Generate an Exception like requests.HTTPError with extra message content"""
    msg = '{} {}: {}'.format(code, _codes[code][0].capitalize(), msg)
    return exception_factory('HTTPError', msg)
