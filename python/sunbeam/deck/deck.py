from .parser     import parse_deck
from collections import Hashable, MutableSequence, Sequence, Iterator
from numbers     import Integral
import copy
import itertools
import traceback

class Cursor( Iterator ):
    def __init__( self, deck, indices, items=None, position=0 ):
        self._deck = deck
        self._indices = indices
        self._items =  items if items else [ deck[ i ] for i in self._indices ]
        self._position = position

    def _index( self, i ):
        self._update( i )
        return self._indices[i]

    @property
    def index( self ):
        return self._index( self._position )

    @property
    def indices( self ):
        return (self._index( i ) for i,_ in enumerate( self._indices ))

    def __len__( self ):
        return len( self._indices )

    def next( self ):
        self._update_all()
        p = self._position + 1
        if p > len( self ):
            raise StopIteration()
        return Cursor( self._deck, self._indices[:], self._items[:], p )

    def __next__( self ):
        return self.next()

    def slice( self, *args ):
        self._update( self._position )
        index = self._indices[ self._position ]
        s = slice(*args)
        start = index + s.start if s.start else None
        stop  = index + s.stop  if s.stop  else None
        step  =         s.step  if s.step  else None
        return slice(start, stop, step)

    def _update( self, i ):
        index = self._indices[i]
        item  = self._items[i]
        if index >= len( self._deck ) or self._deck[ index ] is not item:
            try:
                self._indices[i] = self._deck._id_index( item )
            except Exception as e:
                raise LookupError( "Invalid cursor, has the keyword been removed?" )

    def _update_all( self ):
        for i,_ in enumerate( self._indices ):
            self._update( i )

    @property
    def value( self ):
        return self._items[ self._position ]

    @property
    def values( self ):
        return self._items[:]


class Deck( MutableSequence, Hashable ):

    @staticmethod
    def parse( *args, **kwargs ):
        """Parse a deck from either a string or file.

        Args:
            deck (str): Either an eclipse deck string or path to a file to open.
            keywords (dict|[dict]): List of keyword parser extensions in opm-parser
                format. A description of the opm-parser keyword format can be found
                at: https://github.com/OPM/opm-parser/blob/master/docs/keywords.txt
            recovery ((str, action)|[(str, action)]): List of error recoveries.
                An error recovery is defined by a pair of a string naming the error
                event to be handled and the action taken for this error event. The
                named error event can be one of the following:
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

        Examples:
            Parses a deck from the string "RUNSPEC\\n\\nDIMENS\\n 2 2 1 /\\n"
                deck = sunbeam.parse_deck("RUNSPEC\\n\\nDIMENS\\n 2 2 1 /\\n")
            Parses a deck from the NORNE data set with recovery set to ignore
            PARSE_RANDOM_SLASH error events.
                deck = sunbeam.parse_deck('~/opm-data/norne/NORNE_ATW2013.DATA',
                    recovery=('PARSE_RANDOM_SLASH', sunbeam.action.ignore))

        :rtype: sunbeam.libsunbeam.Deck
        """
        opm_deck = parse_deck( *args, **kwargs )
        def make_kw(opm_kw):
            kw = (opm_kw.name,)
            for record in opm_kw:
                r = [ i for item in record for i in item ]
                if r: kw += (r,)
            if opm_kw.fixed_size:
                kw += ([],)
            return kw
        return Deck( [ make_kw(okw) for okw in opm_deck ] )

    def __init__( self, deck=None ):
        self._kws = deck if deck else []
        class CursorFactory:
            def __init__( s, deck ):
                s.deck = deck
            def __getitem__( s, _key ):
                key = _key[0] if isinstance( _key, tuple ) else _key
                index = _key[1] if isinstance( _key, tuple ) else 0
                if not isinstance( key, str ):
                    raise TypeError( "Deck cursor selection keys must be str, not " + type(key).__name__ )
                if not (isinstance( index, Integral ) or isinstance( index, slice )):
                    raise TypeError( "Deck cursor selection indices must be int or slice, not " + type(index).__name__ )
                indices = s.deck.indices( key )[index]
                indices = indices if isinstance( indices, list ) else [indices]
                if not indices:
                    return None
                return Cursor( s.deck, indices )
        self._cursor_factory = CursorFactory( self )

    def __contains__( self, other ):
        if isinstance( other, str ):
            for kw in self:
                if kw[0] == other:
                    return True
            return False
        else:
            return other in self._kws

    def __delitem__( self, key ):
        if isinstance( key, int ) or isinstance( key, slice ):
            del self._kws[key]
        else:
            raise TypeError( "Deck indices must be integers or slices not " + type(key).__name__ )

    def __eq__( self, other ):
        return self._kws == other._kws

    def __getitem__( self, key ):
        if isinstance( key, int ) or isinstance( key, slice ):
            return self._kws[ key ]
        else:
            raise LookupError( "Invalid deck index: " + repr( key ) )

    def __setitem__( self, key, v ):
        if isinstance( key, int ) or isinstance( key, slice ):
            self._kws[key] = v
        else:
            raise TypeError( "Deck indices must be integers or slices, not " + type(key).__name__ )

    def __hash__( self ):
        return hash(str(self._kws))

    def __iter__( self ):
        return iter( self._kws )

    def __len__( self ):
        return self._kws.__len__()

    def _id_index( self, item ):
        return next( (i for i,v in enumerate(self._kws) if v is item) )

    def count( self, key ):
        if isinstance( key, str ):
            return len( [v for v in self if v[0] == key ] )
        else:
            return self._kws.count( key )

    def data_invariant(self):
        for kw in self._kws:
            assert isinstance(kw, tuple), "Keywords must be tuple instances. Got " + str(type(kw))
            assert len(kw) > 0, "Empty keyword in deck"
            assert isinstance(kw[0], str), "The first element of a keyword must be the keyword name of type str. Got type " + str(type(kw[0]))
            for record in kw[1:]:
                assert isinstance(record, list), "All keyword records must be lists. Got " + str(type(record))
                for item in record:
                    assert isinstance(item, (int, float, str, _repeat)), " Keyword items must be either int, float, str, default or repeat. Got " + str(type(item))

    def index( self, key ):
        return next( (i for i, v in enumerate(self._kws) if v[0] == key) )

    def indices( self, key ):
        return [ i for i, v in enumerate(self._kws) if v[0] == key ]

    def insert( self, key, v ):
        if isinstance( key, int ) or isinstance( key, slice ):
            self._kws.insert( key, v )
        else:
            raise TypeError( "Deck indices must be integers or slices, not " + type(key).__name__ )

    @property
    def select( self ):
        return self._cursor_factory



    def __repr__(self):
        self.data_invariant()
        string = ''
        for kw in self._kws:
            string += Deck.keyword_to_string( kw )
            string += '\n'
        return string

    @staticmethod
    def keyword_to_string( kw ):
        string = ''
        string += kw[0] + '\n'
        for r in kw[1:]:
            string += Deck.record_to_string(r)
        return string

    @staticmethod
    def record_to_string( record ):
        if (record == []):
            return '/\n'
        string = ''
        line = ''
        for item in record + ['/']:
            if line and len(line + repr(item)) > 78:
                string += '  ' + line + '\n'
                line = ''
            item_repr = repr(item) if item != '/' else '/'
            line += item_repr + ' '
        if line:
            string += '  ' + line + '\n'
        return string


class _repeat:
    def __init__(self, default=False, count=None, value=None):
        self.default = default
        self.count = count
        self.value = value

    def __rmul__(self, count):
        r = _repeat(default=self.default, count=count, value=self.value)
        r.data_invariant()
        return r

    def __repr__(self):
        self.data_invariant()
        return '{}*{}'.format(self.count if self.count else '',
                              repr(self.value) if not self.default else '')

    def data_invariant(self):
        if not isinstance(self.default, bool):
            raise ValueError("default parameter must be bool")
        if self.count and not isinstance(self.count, int):
            raise ValueError("Repeat count must be set and int")
        if not self.default and not self.count:
            raise ValueError("Cannot repeat non-default value without count")
        if self.value and not isinstance(self.value, (int, float, str)):
            raise ValueError("Values must be either int, float or str")
        if not self.default and not self.value:
            raise ValueError("Cannot repeat non default item with None value")

def repeat(value):
    return _repeat(value=value)
default = _repeat(default=True)
