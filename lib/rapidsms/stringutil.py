#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

def is_empty(in_str):
    """
    Simple helper to return True if the passed
    string reference is None or '' or all whitespace

    """
    return in_str is None or \
        len(in_str.strip())==0

def not_empty(in_str):
    """
    Simple helper to return True if the passed
    string reference is not empty (as defined
    by 'is_empty' above)

    """
    return not is_empty(in_str)

