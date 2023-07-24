import sys

from loguru import logger

from game_env import GameUnit, UnitType
from step_update import my_methodB

#
#   NOTE:   To run this without SCII, comment out the following in step_update.py
#
#              unit_actions.append(actions.RAW_FUNCTIONS.Move_pt("now", unit_tags[i], (xcor[i],ycor[i])))
#

class GenerateStatsForBlue:

    def __init__(self):
        pass

    def run_my_method_b(self):
        # Create a list of marines
        marine = GameUnit(unit_type=UnitType.Terran_Marine, tag="bob")
        pos = (30, 28)
        marine.set_pos(pos)
        marines = [marine]
        unit_tags = ["bob"]
        num_step = 0
        done = False
        max_step = 100
        while not done and num_step < max_step:
            num_step += 1
            unit_actions, pos, done, reward = my_methodB(num_step, unit_tags, marines, [], [])
            marine.set_pos(pos)
        return num_step, done

    def calc_stats(self):
        num_fail = 0
        steps = []

        logger.remove()
        logger.add(sys.stderr, level="ERROR")

        num_trials = 50000
        for ii in range(num_trials):
            num_steps, done = self.run_my_method_b()
            if done:
                steps.append(num_steps)
            else:
                num_fail += 1
        print(f"Num failed:  {num_fail}")
        from collections import Counter
        counts = Counter(steps)
        print(counts)
        keys = list(counts.keys())
        keys.sort()
        for key in keys:
            print(f" {key} {counts.get(key)/num_trials}")


g = GenerateStatsForBlue()

# do it once
num_step, done = g.run_my_method_b()
print(f"Num steps: {num_step}    Done: {done}")

# do it many times
g.calc_stats()
