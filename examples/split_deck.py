#!/usr/bin/env python
"""\
This program takes an eclipse deck file path as input and outputs an equivalent
deck split into sections.
"""

from __future__ import print_function
import os
from sunbeam.deck import Deck
from sunbeam import action


def split_deck(filename):
    recovery = ('PARSE_RANDOM_SLASH', action.ignore)
    deck = Deck.parse(filename, recovery=recovery)

    sections = [
        'RUNSPEC', 'GRID', 'EDIT', 'PROPS', 'REGIONS', 'SOLUTION', 'SUMMARY',
        'SCHEDULE'
    ]
    sections = [deck.select[section] for section in sections]
    sections = [v for v in sections if v]
    sections.sort(key=lambda cursor: cursor.index)

    written_sections = []
    for fst, snd in zip(sections, sections[1:]) + [(sections[-1], None)]:
        f = fst.index
        s = snd.index if snd else None
        d = Deck(deck[f:s])
        with open(fst.value[0] + ".DATA", "w") as f:
            print(d, file=f)
        written_sections.append(fst.value[0])

    master_deck = Deck()
    for section in written_sections:
        incl = ('INCLUDE', [section + ".DATA"])
        master_deck.append(incl)

    path, extension = os.path.splitext(filename)
    basename = os.path.basename(path)
    with open(basename + "_SPLIT" + extension, "w") as f:
        print(master_deck, file=f)


if __name__ == '__main__':
    from sys import argv
    if len(argv) == 2:
        filename = argv[1]
        split_deck(filename)
    else:
        print('Usage: {} <filename>'.format(argv[0]))
