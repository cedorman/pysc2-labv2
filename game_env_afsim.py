#
# Game Env is an interface to various game implementations.
#
# Default implementation is to keep track of locations internally and move them.   Subclasses
# implement them however it makes sense for their game engine
#
from typing import List

from afsim import Route, Waypoint, Input
from loguru import logger

from AfsimGym import AfsimGym
from game_env import GameEnv, GameUnit, UnitType, INITIAL_RED, INITIAL_BLUE, GameObs, GameAction, ActionType

# Base location for lat/lon.  This is in Iowa somewhere
BASE_LAT = 41.0
BASE_LON = 95.0

# Conversion factor between xy and latlon.  100 means that 1 xy is about 1 km.
CONVERSION_FACTOR = 100.


def convert_xy_to_latlon(xypos):
    """AFSIM uses lat lon, so convert xy to lat lon.   We have to return an altitude, just return 0."""
    lat = BASE_LAT + (xypos[1] / CONVERSION_FACTOR)
    lon = BASE_LON + (xypos[0] / CONVERSION_FACTOR)
    return lat, lon, 0


def convert_latlon_to_xy(latlon):
    x = (latlon[1] - BASE_LON) * CONVERSION_FACTOR
    y = (latlon[0] - BASE_LAT) * CONVERSION_FACTOR
    return x, y


class GameEnvAFSIM(GameEnv):

    def __init__(self):
        super().__init__()
        self.gym = None

    def reset(self):
        """Reset the game.  Return 2 obs, one for each agent"""

        self.gym = AfsimGym(scenario_file="delta-ai/Simulations/DELTA/training/mine_hunter_template.txt",
                            aer_name="pysc2-labv2",
                            output_aer=True)
        self.sim_time = 0
        self.sim_frame_time = .25

        self.steps = 0
        self.max_steps = 100

        self.red_forces = []
        self.blue_forces = []

        for ii in range(1):
            unit_tag = "red_" + str(ii)
            red_unit = GameUnit(UnitType.Terran_Marine, unit_tag)
            red_unit.set_pos(INITIAL_RED)
            self.red_forces.append(red_unit)

            latlon = convert_xy_to_latlon(INITIAL_RED)
            self.gym.add_platform(unit_tag, "DELTA_REMUS100_PLATFORM", (latlon[0], latlon[1], 0))

        for ii in range(1):
            unit_tag = "blue_" + str(ii)
            blue_unit = GameUnit(UnitType.Terran_Marine, 'blue_' + str(ii))
            blue_unit.set_pos(INITIAL_BLUE)
            self.blue_forces.append(blue_unit)

            latlon = convert_xy_to_latlon(INITIAL_BLUE)
            self.gym.add_platform(unit_tag, "DELTA_REMUS100_PLATFORM", (latlon[0], latlon[1], 0))

        # Return the observations
        return self._get_obs()

    def _get_obs(self):
        agent1_obs = GameObs()
        agent1_obs.set_units(self.red_forces)
        agent2_obs = GameObs()
        agent2_obs.set_units(self.blue_forces)

        # TODO:  get info from AFSIM

        return [agent1_obs, agent2_obs]

    def _move_action(self, unit_tag, new_pos):
        """Move a unit to position (instantly).
        WARNING:  This does not check to make sure the move is valid.  """
        for unit in self.red_forces:
            if unit.tag == unit_tag:
                unit.set_pos(new_pos)
                logger.info(f"Moved unit {unit_tag} to new pos {new_pos}")

                self._move_in_afsim(unit_tag, new_pos)

                return

        for unit in self.blue_forces:
            if unit.tag == unit_tag:
                unit.set_pos(new_pos)
                logger.info(f"Moved unit {unit_tag} to new pos {new_pos}")

                self._move_in_afsim(unit_tag, new_pos)

                return
        logger.warning(f"Unable to find unit {unit_tag} to move it!!!")

    def step(self, actions: List[List[GameAction]]):

        self.sim_time += self.sim_frame_time
        self.gym.advance_time(self.sim_time)
        logger.info("Sim time: ", self.gym.sim.get_sim_time())

        platform_names = self.gym.sim.get_platforms()
        for platform_name in platform_names:

            platform = self.gym.sim.get_platform_by_name(platform_name)
            lla = platform.get_location_lla()
            xy = convert_latlon_to_xy(lla)
            logger.info(f"Platform: {platform}.  position {lla} -> {xy}")

        self.steps += 1

        for action_list in actions:
            for action in action_list:
                if action.action_type == ActionType.MOVE:
                    self._move_action(action.unit_tag, action.pos)
                logger.info(f"Taking action at step {self.steps}: {action}")

        observations = self._get_obs()
        if self.steps >= self.max_steps:
            for obs in observations:
                obs.set_last(True)

        return observations

    def _move_in_afsim(self, unit_tag, new_pos):
        """Move a unit in AFSIM.  The way we do this is to create a Route with a new Waypoint
        at the new position and tell AFSIM to set the route at the current sim time"""

        latlon_position = convert_xy_to_latlon(new_pos)
        #
        # lat = latlon_position[0]
        # lat_hem = "n"
        # lon = latlon_position[1]
        # lon_hem = "e"
        #
        # if latlon_position[0] < 0:
        #     lat = latlon_position[0] * -1
        #     lat_hem = 's'
        # if latlon_position[1] < 0:
        #     lon = latlon_position[1] * -1
        #     lon_hem = 'w'

        # route = Route()
        # wp = Waypoint(lat=latlon_position[0], lon=latlon_position[1], alt=latlon_position[2], speed=0)
        # route.append(wp)
        #
        # platform = self.gym.sim.get_platform_by_name(unit_tag)
        #
        # # new_plat.set_location_lla( lat=position[0], lon=position[1], alt=position[2] )
        # afsim_input = Input(f"position {lat}{lat_hem} {lon}{lon_hem}")
        # platform.process_input(afsim_input)
        #
        # mover = platform.get_mover()
        # if mover:
        #     platform.get_mover().set_route(self.gym.sim.get_sim_time(), route)
        # else:
        #     logger.warning(f"platform {unit_tag} is not a mover")

        platform = self.gym.sim.get_platform_by_name(unit_tag)
        platform.set_location_lla(latlon_position[0], latlon_position[1], 0)