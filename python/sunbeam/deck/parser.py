from os.path import isfile
import json
from .. import libsunbeam as lib
from .. import parser

def parse_deck(deck, keywords=[], recovery=[]):
    if keywords:
        # this might be a single keyword dictionary, in which case we pack it
        # into a list. If it's not a dict we assume it's an iterable and just
        # carry on
        if isinstance(keywords, dict):
            keywords = [keywords]
        keywords = map(json.dumps, keywords)
    is_file = isfile(deck) # If the deck is a file, the deck is read from
                           # that file. Otherwise it is assumed to be a
                           # string representation of the the deck.
    pc = parser._parse_context(recovery) if recovery else lib.ParseContext()
    return lib.parse_deck(deck, keywords, is_file, pc)
