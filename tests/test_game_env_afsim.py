from unittest import TestCase

from game_env import INITIAL_RED, INITIAL_BLUE
from game_env_afsim import convert_xy_to_latlon, convert_latlon_to_xy


class Test(TestCase):
    def test_convert_xy_to_latlon(self):
        xypos = INITIAL_BLUE
        print(f"xy {xypos}")

        latlon = convert_xy_to_latlon(xypos)
        print(f"latlon:  {latlon}")

        newxypos = convert_latlon_to_xy(latlon)
        print(f"new xy {newxypos}")

        self.assertAlmostEqual(xypos[0], newxypos[0], msg="X Not close enough", delta=0.00001)
        self.assertAlmostEqual(xypos[1], newxypos[1], msg="Y Not close enough", delta=0.00001)
