"""Functions to help parse strings into datetime objects"""
import dateparser


def parse_human_readable_time(time_string):
    """Parse human readable strings (e.g. "now", "2017-01-01" and "one hour ago") into datetime"""
    return dateparser.parse(time_string, settings={'RETURN_AS_TIMEZONE_AWARE': True})
