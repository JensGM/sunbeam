#!/usr/bin/env python

from __future__ import print_function
import sys
from sunbeam.deck import Deck
from sunbeam      import action

def split_deck( file_name ):
    recovery = ('PARSE_RANDOM_SLASH', action.ignore)
    deck = Deck.parse( file_name, recovery=recovery )

    sections = [ deck.select[ 'RUNSPEC'  ],
                 deck.select[ 'GRID'     ],
                 deck.select[ 'EDIT'     ],
                 deck.select[ 'PROPS'    ],
                 deck.select[ 'REGIONS'  ],
                 deck.select[ 'SOLUTION' ],
                 deck.select[ 'SUMMARY'  ],
                 deck.select[ 'SCHEDULE' ] ]

    sections = [ v for v in sections if v ]
    sections.sort( key=lambda cursor: cursor.index )

    for fst, snd in zip( sections, sections[1:] ):
        with open( fst.value[0] + ".DATA", "w" ) as f:
            print( Deck( deck[ fst.index : snd.index ] ), file=f )

if __name__ == '__main__':
    file_name = sys.argv[1] if len( sys.argv ) == 2 else \
        '../../opm-data/norne/NORNE_ATW2013.DATA'
    split_deck( file_name )
