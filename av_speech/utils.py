# Collection of low level converters to/from objective C
from .objc_util import ObjCInstance

__all__ = ["ns_string_to_py_string"]


def ns_string_to_py_string(ns_string: ObjCInstance) -> str:
    """Low level function to convert NSString (or subclass thereof) input
    to a python `str`.
    Confirmed to work work on:
    - NSString
    - NSTaggedPointerString
    - NSMutableString
    :param ns_string: A NSString to convert
    :return: The converted string as Python `str`.
    """
    return ns_string.UTF8String().decode("utf-8")