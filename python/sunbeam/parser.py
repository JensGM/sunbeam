from os.path import isfile
import json
import libsunbeam as lib
from .properties import EclipseState


def _parse_context(recovery):
    ctx = lib.ParseContext()

    if not recovery:
        return ctx

    # this might be a single tuple, in which case we unpack it and repack it
    # into a list. If it's not a tuple we assume it's an iterable and just
    # carry on
    if not isinstance(recovery, list):
        recovery = [recovery]

    for key, action in recovery:
        ctx.update(key, action)

    return ctx


def parse(deck, recovery=[]):
    """Parse a deck from either a string or file.

    Args:
        deck (str): Either an eclipse deck string or path to a file to open.
        recovery ((str, action)|[(str, action)]): List of error recoveries.
            An error recovery is defined by a pair of a string naming the error
            event to be handled and the action taken for this error event.
            The named error event can be one of the following:
                "PARSE_UNKNOWN_KEYWORD"
                "PARSE_RANDOM_TEXT"
                "PARSE_RANDOM_SLASH"
                "PARSE_MISSING_DIMS_KEYWORD"
                "PARSE_EXTRA_DATA"
                "PARSE_MISSING_INCLUDE"
                "UNSUPPORTED_SCHEDULE_GEO_MODIFIER"
                "UNSUPPORTED_COMPORD_TYPE"
                "UNSUPPORTED_INITIAL_THPRES"
                "UNSUPPORTED_TERMINATE_IF_BHP"
                "INTERNAL_ERROR_UNINITIALIZED_THPRES"
                "SUMMARY_UNKNOWN_WELL"
                "SUMMARY_UNKNOWN_GROUP"
            The avaiable recovery actions can be one of the following:
                sunbeam.action.throw
                sunbeam.action.warn
                sunbeam.action.ignore

    Example:
        Parses a EclipseState from the NORNE data set with recovery set to
        ignore PARSE_RANDOM_SLASH error events.
            es = sunbeam.parse('~/opm-data/norne/NORNE_ATW2013.DATA',
                recovery=('PARSE_RANDOM_SLASH', sunbeam.action.ignore))

    :rtype: EclipseState
    """
    if isfile(deck):
        return EclipseState(lib.parse(deck, _parse_context(recovery)))
    return EclipseState(lib.parse_data(deck, _parse_context(recovery)))
