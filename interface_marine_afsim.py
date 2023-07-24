import time

from absl import app
from loguru import logger
from pysc2.env import sc2_env
from pysc2.lib import features

import observ
import step_update_game as step_update_interface
from game_env import UnitType, GameObs, GameEnv
from game_env_afsim import GameEnvAFSIM

file1Name = 'fileEach15000_times.txt'
file2Name = 'file15000.txt'


def get_raw_units_by_type(obs: GameObs, unit_type):
    return [unit for unit in obs.get_raw_units() if unit.get_unit_type() == unit_type]


## Red Agent (Our Agent)
class TerranAgent1:

    def __init__(self):
        self.attack_coordinates = None
        self.marine_tag1 = None
        # self.marine_tag2 = None
        self.tank_tag = None
        self.num_step = 0

    def setup(self, unused1, unused2):
        pass

    def reset(self):
        pass

    def step(self, obs: GameObs, blue_pos):

        marines = get_raw_units_by_type(obs, UnitType.Terran_Marine)

        if self.marine_tag1 == None:
            if len(marines) <= 0:
                logger.warning("No marines!")
                return [], False, 0
            self.marine_tag1 = marines[0].tag
        marine = []
        xcor = []
        ycor = []

        unit_tags = [self.marine_tag1]
        marine.append([unit for unit in marines if unit.tag == self.marine_tag1][0])
        unit_actions, done, reward = step_update_interface.my_methodR(self.num_step, unit_tags, marine, xcor, ycor,
                                                                      blue_pos)
        self.num_step += 1
        return unit_actions, done, reward


## Blue Agent (Opponent)
class TerranAgent2:

    def __init__(self):
        self.attack_coordinates = None
        self.marine_tag3 = None
        self.tank_tag = None
        self.num_step = 0
        self.pos = (20, 20)

    def setup(self, unused1, unused2):
        pass

    def reset(self):
        self.pos = (20, 20)

    def step(self, obs):
        # super(TerranAgent2, self).step(obs)
        marines = get_raw_units_by_type(obs, UnitType.Terran_Marine)
        if (self.marine_tag3 == None):
            if len(marines) <= 0:
                logger.warning("No marines!")
                return [], (0, 0), False, 0
            self.marine_tag3 = marines[0].tag
        marine = []

        unit_actions = []
        unit_tags = [self.marine_tag3]
        marine.append([unit for unit in marines if unit.tag == self.marine_tag3][0])
        unit_actions, pos, done, reward = step_update_interface.my_methodB(self.num_step, unit_tags, marine)
        self.num_step += 1
        return unit_actions, pos, done, reward


def get_game_env():
    env = GameEnv()
    return env


def get_afsim_env():
    env = GameEnvAFSIM()
    return env


def get_scii_env():
    env = sc2_env.SC2Env(
        map_name="Base_Map_no_attack",
        players=[sc2_env.Agent(sc2_env.Race.terran),
                 sc2_env.Agent(sc2_env.Race.terran)],
        agent_interface_format=features.AgentInterfaceFormat(
            feature_dimensions=features.Dimensions(screen=84, minimap=64),
            use_feature_units=True,
            use_raw_units=True,
            use_raw_actions=True,
            # rgb_dimensions=None
            rgb_dimensions=sc2_env.Dimensions(screen=256, minimap=256)
        ),
        # score_index=0,
        step_mul=100,
        game_steps_per_episode=0,
        visualize=True)
    # visualize=False
    return env


def main(unused_argv):
    agent1 = TerranAgent1()
    agent2 = TerranAgent2()
    observ.printloc()
    winner_blue_cnt = 0
    winner_red_cnt = 0
    episodes = 100
    logger.info("Starting " + str(episodes) + " Run experiment")
    try:
        with get_afsim_env() as env:
            agent1.setup(env.observation_spec(), env.action_spec())
            agent2.setup(env.observation_spec(), env.action_spec())
            with open(file1Name, 'a') as ff:
                ff.write("Trials with Visualization + Prints + Rewards" + '\n')
            for tt in range(episodes):
                start = time.time()
                timesteps = env.reset()
                agent1.reset()
                agent2.reset()
                step_num = 0
                ep_reward = 0
                pos = (30, 28)
                while True:
                    agent1_actions, doneR, reward1 = agent1.step(timesteps[0], pos)
                    agent2_actions, pos, doneB, reward2 = agent2.step(timesteps[1])
                    step_actions = [agent1_actions, agent2_actions]
                    ep_reward += (reward1 + reward2)
                    ## If red agent reaches the blue base stop
                    if doneR:
                        winner_red_cnt += 1
                        logger.info(f"--------------------- RED WINS --episode: {tt} --- {step_num} -------- {winner_red_cnt}")
                        with open(file1Name, 'a') as ff:
                            ff.write("Trial " + str(tt) + " Winner: Red" + '\t')
                        break
                    if doneB:
                        winner_blue_cnt += 1
                        logger.info(f"--------------------- BLUE WINS --episode {tt} ---------- {winner_blue_cnt}")
                        with open(file1Name, 'a') as ff:
                            ff.write("Trial " + str(tt) + " Winner: Blue" + '\t')
                        break

                    if timesteps[0].get_last():
                        break
                    timesteps = env.step(step_actions)
                    step_num = step_num + 1
                with open(file1Name, 'a') as ff:
                    ff.write("Time:" + str(time.time() - start) + "\t")
                    ff.write("Total Reward:" + str(ep_reward) + "\n")
        line = "Win Percentage:" + str(winner_red_cnt)
        with open(file2Name, 'w') as f:
            f.write(line + '\n')
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app.run(main)
