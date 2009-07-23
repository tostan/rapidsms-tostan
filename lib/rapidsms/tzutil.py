#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import pytz
from datetime import datetime

"""
Some simple utility calls for dealing datetime and timedelta
objects.

In particular for converting TZ naive and TZ aware datetimes 

"""

def to_naive_utc(dt):
    """
    Converts a datetime to a naive datetime (no tzinfo) 
    as follows:

    if inbound dt is already naive, it just returns it
    
    if inbound is timezone aware, converts it to UTC,
    then strips the tzinfo

    """
    if not isinstance(dt, datetime):
        raise ValueError("Must supply datetime object")

    if dt.tzinfo is None:
        return dt

    return dt.astimezone(pytz.utc).replace(tzinfo=None)

def to_aware_utc(dt):
    """
    Convert an inbound datetime into a timezone
    aware datetime in UTC as follows:

    if inbound is naive, uses 'tzinfo.localize' to
    add utc tzinfo. NOTE: Timevalues are not changed,
    only difference in tzinfo is added to identify this
    as a UTC tz aware object.

    if inbound is aware, uses 'datetime.astimezone'
    to convert timevalues to UTC and set tzinfo to
    utc.

    """
    if not isinstance(dt, datetime):
        raise ValueError("Must supply datetime object")

    if dt.tzinfo is None:
        return pytz.utc.localize(dt)

    return dt.astimezone(pytz.utc)


def timedelta_as_minutes(td):
    """
    Returns the value of the entire timedelta as
    integer minutes, rounded down
    
    """
    return timedelta_as_seconds(td)/60


def timedelta_as_seconds(td):
    '''
    Returns the value of the entire timedelta as
    integer seconds, rounded down
    
    '''
    return td.days*86400+td.seconds
    
