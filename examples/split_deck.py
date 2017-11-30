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

    sections_names = [
        'RUNSPEC', 'GRID', 'EDIT', 'PROPS', 'REGIONS', 'SOLUTION', 'SUMMARY',
        'SCHEDULE'
    ]
    cursors = [deck.select[s] for s in sections_names]
    sections = [next(c) for c in cursors if c]
    sections.sort(key=lambda s: s[0])

    written_sections = []
    for s0, s1 in zip(sections, sections[1:]) + [(sections[-1], None)]:
        start, section = s0
        stop = s1[0] if s1 else None
        d = Deck(deck[start:stop])

        section_name = section[0]
        with open(section_name + ".DATA", "w") as f:
            print(d, file=f)
        written_sections.append(section_name)

    master_deck = Deck()
    for section in written_sections:
        include = ('INCLUDE', [section + ".DATA"])
        master_deck.append(include)

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
