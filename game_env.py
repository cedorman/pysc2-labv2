#
# Game Env is an interface to various game implementations.
#
# Default implementation is to keep track of locations internally and move them.   Subclasses
# implement them however it makes sense for their game engine
#
from enum import Enum
from typing import List

from loguru import logger

INITIAL_BLUE = (30, 28)
INITIAL_RED = (95, 95)


class UnitType(Enum):
    Terran_Marine = 1
    Other = 2


class ActionType(Enum):
    MOVE = 1


class GameUnit:
    """A 'unit' is an individual element in a game, such as a piece or marine

    Units have types (one of an enum) and a tag (string)
    """

    def __init__(self, unit_type=None, tag=None):
        if unit_type is None:
            self.unit_type: UnitType = UnitType.Other
        else:
            self.unit_type = unit_type
        if tag is None:
            self.tag = 'unknown_tag'
        else:
            self.tag = tag
        self.pos = (-1, -1)
        self.x = self.pos[0]
        self.y = self.pos[1]

    def get_unit_type(self) -> UnitType:
        return self.unit_type

    def get_tag(self) -> str:
        return self.tag

    def set_pos(self, new_pos):
        self.pos = new_pos
        self.x = self.pos[0]
        self.y = self.pos[1]

    def get_pos(self):
        return self.pos


class GameObs:
    """What is observed by a particular agent.  This will vary by agent.  """

    def __init__(self):
        self.units = []
        self.is_last = False

    def get_raw_units(self) -> List[GameUnit]:
        return self.units

    def set_units(self, units: List[GameUnit]):
        self.units = units

    def get_last(self):
        """Is this the last obseravation"""
        return self.is_last

    def set_last(self, new_last):
        self.is_last = new_last


class GameState:

    def __init__(self):
        pass


class GameAction:
    """Represent an action a unit can take, like move, fire, etc.  """

    def __init__(self, unit_tag, action_type: ActionType, *args, **kwargs):
        """Create an action"""
        self.action_type = action_type
        self.unit_tag = unit_tag
        self.pos = None

        pos = kwargs.get('pos', None)
        if self.action_type == ActionType.MOVE and pos is not None:
            logger.info(f"Moving {unit_tag} to {pos}")
            self.pos = pos
            return

    def __str__(self):
        out_str = f"{self.action_type} on {self.unit_tag}"
        if self.pos is not None:
            out_str += f" to {self.pos}"
        return out_str


class GameEnv:
    def __init__(self):
        self.reset()

    def __enter__(self):
        """Function necessary to do a 'with' command."""
        return self

    def __exit__(self, type, value, traceback):
        """Function necessary to do a 'with' command."""
        pass

    def observation_spec(self):
        pass

    def action_spec(self):
        pass

    def reset(self):
        """Reset the game.  Return 2 obs, one for each agent"""

        self.steps = 0
        self.max_steps = 100

        self.red_forces = []
        self.blue_forces = []

        for ii in range(1):
            red_unit = GameUnit(UnitType.Terran_Marine, 'red_' + str(ii))
            red_unit.set_pos(INITIAL_RED)
            self.red_forces.append(red_unit)

        for ii in range(1):
            blue_unit = GameUnit(UnitType.Terran_Marine, 'blue_' + str(ii))
            blue_unit.set_pos(INITIAL_BLUE)
            self.blue_forces.append(blue_unit)

        # Return the observations
        return self._get_obs()

    def _get_obs(self):
        agent1_obs = GameObs()
        agent1_obs.set_units(self.red_forces)
        agent2_obs = GameObs()
        agent2_obs.set_units(self.blue_forces)
        return [agent1_obs, agent2_obs]

    def _move_action(self, unit_tag, new_pos):
        """Move a unit to position (instantly).
        WARNING:  This does not check to make sure the move is valid.  """
        for unit in self.red_forces:
            if unit.tag == unit_tag:
                unit.set_pos(new_pos)
                logger.info(f"Moved unit {unit_tag} to new pos {new_pos}")
                return
        for unit in self.blue_forces:
            if unit.tag == unit_tag:
                unit.set_pos(new_pos)
                logger.info(f"Moved unit {unit_tag} to new pos {new_pos}")
                return
        logger.warning(f"Unable to find unit {unit_tag} to move it!!!")

    def step(self, actions: List[List[GameAction]]):

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
