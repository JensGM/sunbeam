#!/usr/bin/env python

from __future__ import print_function

import sys
from datetime import date
from itertools import chain, dropwhile, takewhile
from sunbeam import action
from sunbeam.deck import Deck

def not_date(kw):
    return kw[0] != "DATES"

def fragment_date(f):
    month = {
        "JAN":1, "FEB":2, "MAR":3, "APR":4, "MAI":5, "MAY":5, "JUN":6, "JLY":7,
        "JUL":7, "AUG":8, "SEP":9, "OCT":10, "OKT":10, "NOV":11, "DEC":12,
        "DES":12,
    }[f[0][1][1]]
    return date(year=f[0][1][2], month=month, day=f[0][1][0])

def main(args):
    pargs = { 'recovery' : ('PARSE_RANDOM_SLASH', action.ignore) }
    fragments = [ Deck.parse(a, **pargs) for a in args ]
    merged = list(chain(*fragments))

    dates = []
    xs = list(dropwhile(not_date, merged))
    while xs:
        x, y = xs[0], xs[1:]
        xs = list(dropwhile(not_date, y))
        dates.append([x] + list(takewhile(not_date, y)))

    xs = list(takewhile(not_date, merged))
    dates.sort(key=fragment_date)

    d = Deck(list(chain(xs, *dates)))
    with open('out', 'w') as f:
        print(d, file=f)

if __name__ == '__main__':
    main(sys.argv[1:])
