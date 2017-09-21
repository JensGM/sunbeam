from __future__ import print_function
import unittest
from sunbeam.deck import Deck, repeat, default
from textwrap import dedent


class TestMutableDeck(unittest.TestCase):
    def setUp(self):
        self.deck_string = dedent("""\
            START             -- 0
              10 MAI 2007 /
            RUNSPEC

            DIMENS
              2 2 1 /
            GRID
            DX
              4*0.25 /
            DY
              4*0.25 /
            DZ
              4*0.25 /
            TOPS
              4*0.25 /
            REGIONS
            OPERNUM
              3 3 1 2 /
            FIPNUM
              1 1 2 3 /
            PARALLEL
              1 "DISTRIBUTED" /
            GRID
            GRID
            GRID
            """)

    def test_parse(self):
        deck = Deck.parse(self.deck_string)
        self.assertEqual(len(deck), 15)

    def test_count(self):
        deck = Deck.parse(self.deck_string)
        self.assertEqual(deck.count('GRID'), 4)
        self.assertEqual(deck.count('GRID'), deck.count(('GRID', )))

    def test_insert(self):
        deck = Deck.parse(self.deck_string)
        self.assertNotIn('NOSIM', deck)
        deck.insert(deck.select['RUNSPEC'].index + 1, ('NOSIM', ))
        self.assertIn('NOSIM', deck)

    def test_slice(self):
        deck = Deck.parse(self.deck_string)
        self.assertNotIn('NOSIM', deck)
        self.assertNotIn('OPTIONS', deck)
        self.assertEqual(deck.count('OPTIONS'), 0)
        deck[deck.select['RUNSPEC'].slice(1, 1)] = [('NOSIM', ), ('OPTIONS', [
            85 * default, 1
        ]), ('OPTIONS', [231 * default, 1])]
        self.assertIn('NOSIM', deck)
        self.assertIn('OPTIONS', deck)
        self.assertEqual(deck.count('OPTIONS'), 2)

    def test_indexing(self):
        deck = Deck.parse(self.deck_string)
        self.assertEqual(deck.count('GRID'), 4)
        grid0 = deck.select['GRID', 0]
        grid1 = deck.select['GRID', 1]
        grid2 = deck.select['GRID', 2]
        grid3 = deck.select['GRID', 3]
        deck[grid0.index] = ('SWAPPED', )
        deck[grid1.index] = ('SWAPPED', )
        deck[grid2.index] = ('SWAPPED', )
        deck[grid3.index] = ('SWAPPED', )
        self.assertEqual(deck.count('GRID'), 0)
        self.assertEqual(deck.count('SWAPPED'), 4)
        for i in deck.select['SWAPPED', :].indices:
            deck[i] = ('GRID', )
        self.assertEqual(deck.count('GRID'), 4)
        self.assertEqual(deck.count('SWAPPED'), 0)

    def test_del(self):
        deck = Deck.parse(self.deck_string)
        self.assertIn('GRID', deck)
        self.assertEqual(deck.count('GRID'), 4)
        for i in deck.select['GRID', :].indices:
            del deck[i]
        self.assertNotIn('GRID', deck)
        self.assertEqual(deck.count('GRID'), 0)

    def test_repeat(self):
        o = 85 * default
        d = 4 * repeat(0.25)
        self.assertEqual(o.default, True)
        self.assertEqual(o.count, 85)
        self.assertEqual(o.value, None)
        self.assertEqual(d.default, False)
        self.assertEqual(d.count, 4)
        self.assertEqual(d.value, 0.25)

    def test_output_simple(self):
        deck = Deck()
        deck.append(('OPTIONS', [85 * default, 1]))
        deck.append(('DX', [4 * repeat(0.25)]))
        options_str = Deck.keyword_to_string(deck.select['OPTIONS'].value)
        dx_str = Deck.keyword_to_string(deck.select['DX'].value)
        self.assertEqual(options_str, "OPTIONS\n  85* 1 / \n")
        self.assertEqual(dx_str, "DX\n  4*0.25 / \n")

    def test_output_reparse(self):
        deck0 = Deck.parse(self.deck_string)
        deck1 = Deck.parse(str(deck0))
        self.assertEqual(deck0, deck1)
