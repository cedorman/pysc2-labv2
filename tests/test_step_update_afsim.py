from unittest import TestCase

import numpy

from step_update_game import get_loc_from_pos


class Test(TestCase):
    def test_get_loc_from_pos(self):
        """ Test converting from a position to a location. """

        # Checking X.    0 -> 0, 30->0, 105 -> 7
        position = (0, 0)
        loc = get_loc_from_pos(position)
        self.assertEqual(0, loc[0], f'X is wrong for {position}')
        self.assertEqual(7, loc[1], f'Y is wrong for {position}')

        position = (30, 0)
        loc = get_loc_from_pos(position)
        self.assertEqual(0, loc[0], f'X is wrong for {position}')
        self.assertEqual(7, loc[1], f'Y is wrong for {position}')

        position = (105, 0)
        loc = get_loc_from_pos(position)
        self.assertEqual(7, loc[0], f'X is wrong for {position}')
        self.assertEqual(7, loc[1], f'Y is wrong for {position}')

        position = (99, 0)
        loc = get_loc_from_pos(position)
        self.assertEqual(6, loc[0], f'X is wrong for {position}')
        self.assertEqual(7, loc[1], f'Y is wrong for {position}')

        # Checking 7.    0 -> 7, 30->7,  105 -> 0
        position = (0, 0)
        loc = get_loc_from_pos(position)
        self.assertEqual(0, loc[0], f'X is wrong for {position}')
        self.assertEqual(7, loc[1], f'Y is wrong for {position}')

        position = (0, 105)
        loc = get_loc_from_pos(position)
        self.assertEqual(0, loc[0], f'X is wrong for {position}')
        self.assertEqual(0, loc[1], f'Y is wrong for {position}')

        position = (0, 30)
        loc = get_loc_from_pos(position)
        self.assertEqual(0, loc[0], f'X is wrong for {position}')
        self.assertEqual(7, loc[1], f'Y is wrong for {position}')

        for y in numpy.arange(0, 130, 5):
            position = (0, y)
            loc = get_loc_from_pos(position)
            print(f" {y} {loc[1]}")
