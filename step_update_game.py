#
# Encapsulate logic about what the units are doing.
#
# We are using two descriptions for where the units are.
#   pos -- 'position' in game space.  2-d, could be float or int, any value.
#   loc -- 'location' in logic space.  2-d, int between 0 and 7 (inclusive)
#
# Original comments:
##
## A simple Wrapper for interfacing with PySC2 as a grid world
## the move selector methods also provide information about the rewards
import random as rng

import numpy as np
from loguru import logger

from game_env import GameAction, ActionType

## Read Learned Policy as a Q table from pkl file
with open('pr-qtable.npy', 'rb') as fp:
    q_table = np.load(fp)

directions = ['up', 'down', 'left', 'right']

## Game setup
red_base = (7, 0)
blue_base = (0, 7)
mountains = [(2, 3), (3, 3), (2, 4), (3, 4), (4, 4), (4, 5)]
## Grid size
size = 8


def validMove(loc, direction):
    if direction == 'nop':
        return True
    elif direction == 'up':
        new_pos = (loc[0], loc[1] + 1)
    elif direction == 'down':
        new_pos = (loc[0], loc[1] - 1)
    elif direction == 'left':
        new_pos = (loc[0] - 1, loc[1])
    elif direction == 'right':
        new_pos = (loc[0] + 1, loc[1])
    else:
        new_pos = (loc[0], loc[1])
    if new_pos[0] < 0 or new_pos[1] < 0 or new_pos[0] > size - 1 or new_pos[1] > size - 1:
        logger.warning(f"Attempting to move unit to {loc} illegally")
        return False
    if new_pos in mountains:
        logger.warning(f"Attempting to move unit to mountains")
        return False
    return True


def check_loc_range(val, low_inclusive: int, high_inclusive: int) -> int:
    if val < low_inclusive:
        logger.warning(f"Value {val} was out of range.  Setting to {low_inclusive}")
        return low_inclusive
    if val > high_inclusive:
        logger.warning(f"Value {val} was out of range.  Setting to {high_inclusive}")
        return high_inclusive
    return val


def get_loc_from_pos(pos: (float, float)) -> (int, int):
    """Convert a 'position' (somewhere on game grid, could be floats) to 'location', integer range (0-7, 0-7) """
    x_co = (pos[0] - 30) // 10
    y_co = abs((pos[1] - 28) // 10 - 7)

    x_co = check_loc_range(x_co, 0, 7)
    y_co = check_loc_range(y_co, 0, 7)

    return x_co, y_co


def get_new_pos_from_direction(current_pos, direction):
    """Given direction, compute the new position in game space.  For use in game actions."""
    new_x = current_pos[0]
    new_y = current_pos[1]
    if direction == "up":
        new_y = int(new_y) - 10
    elif direction == "down":
        new_y = int(new_y) + 10
    elif direction == "left":
        new_x = int(new_x) - 10
    elif direction == "right":
        new_x = int(new_x) + 10
    else:
        logger.warning(f"Unrecognized step! {direction}")
    return new_x, new_y


def my_methodB(num_step, unit_tags, marine):
    """ method for Blue agent.  Opponent Blue agent moves with a stochastic greedy policy based on
    its current manhattan distance from red base """

    blue_pos = (marine[0].x, marine[0].y)
    blue_loc = get_loc_from_pos(blue_pos)

    direction = 'nop'
    if rng.randint(0, 9) < 3:
        direction = rng.choice(directions)
        if not validMove(blue_loc, direction):
            direction = "nop"
    else:
        x_dis = blue_loc[0] - red_base[0]
        if x_dis > 0:
            direction = 'left'
        elif x_dis < 0:
            direction = 'right'
        else:
            y_dis = blue_loc[1] - red_base[1]
            if y_dis > 0:
                direction = 'down'
            elif y_dis < 0:
                direction = 'up'
        if not validMove(blue_loc, direction):
            direction = rng.choice(directions)
            if not validMove(blue_loc, direction):
                direction = ["nop"]

    agent_step = [direction]

    unit_actions = []

    logger.info(f"At step: {num_step} BLUE position: {blue_pos} location: {blue_loc} took action: {agent_step}")

    done = False
    reward = 0
    for i in range(1):

        current_pos = (marine[i].x, marine[i].y)
        new_blue_pos = get_new_pos_from_direction(current_pos, agent_step[i])
        blue_loc = get_loc_from_pos(new_blue_pos)
        if blue_loc == red_base:
            done = True

        # unit_actions.append(actions.RAW_FUNCTIONS.Move_pt("now", unit_tags[i], (new_x, new_y)))
        unit_actions.append(GameAction(unit_tags[i], ActionType.MOVE, pos=new_blue_pos))

        result = {"unit tag": [unit_tags[i]], "location": list(new_blue_pos)}
        logger.info("Blue:", result)
        if done:
            reward = -100
    return unit_actions, new_blue_pos, done, reward


def my_methodR(num_step, unit_tags, marine, xcor, ycor, blue_pos):
    """ ## method for red agent. Move Red agent based on the learned policy by consulting the Q table """
    unit_actions = []

    red_pos = (marine[0].x, marine[0].y)
    red_loc = get_loc_from_pos(red_pos)

    logger.info(f"At step: {num_step} RED position {red_pos}   location: {red_loc}")

    blue_loc = get_loc_from_pos(blue_pos)
    logger.info(f"And Opponent location: {blue_loc}")


    ## Agents current location and opponents locations are used as state information
    ## to access the action Q values to select the best performing action
    q_vals = q_table[red_loc[0]][red_loc[1]][blue_loc[0]][blue_loc[1]]
    logger.info(f"Q values {q_vals}")
    agent_step = [directions[np.argmax(q_vals)]]
    reward = 0
    if not validMove(red_loc, agent_step[0]):
        agent_step = ["nop"]
        reward = -10
    else:
        reward = -1

    logger.info(f"At step took action: {agent_step}")
    # time.sleep(1)
    done = False
    for i in range(1):

        current_pos = (marine[i].x, marine[i].y)
        new_red_pos = get_new_pos_from_direction(current_pos, agent_step[i])
        red_loc = get_loc_from_pos(new_red_pos)
        if red_loc == blue_base:
            done = True

        # unit_actions.append(actions.RAW_FUNCTIONS.Move_pt("now", unit_tags[i], (new_x, new_y)))
        unit_actions.append(GameAction(unit_tags[i], ActionType.MOVE, pos=new_red_pos))

        result = {"unit tag": [unit_tags[i]], "location": list(new_red_pos)}
        logger.info("R:", result)
    if done:
        reward = 100
    return unit_actions, done, reward
