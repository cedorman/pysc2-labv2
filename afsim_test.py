import os

import numpy as np

from AfsimGym import AfsimGym

CAFSIM_ROOT = "home/cdorman/work/neurosymbolic/delta/AFSIM_v2.8.1_C_AFSIM/"
os.environ[CAFSIM_ROOT] = CAFSIM_ROOT

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)


def gen_random_pos():
    lat = np.random.uniform(low=41.9, high=42.0)
    lon = np.random.uniform(low=-72.0, high=-71.85)

    return lat, lon


def main():
    # all these directories were relative to running this code in delta-phase2/ main repo directory
    # should probably use absolute paths anyways, but you'll need to change these or move this file.
    gym = AfsimGym(scenario_file="delta-ai/Simulations/DELTA/training/mine_hunter_template.txt",
                   aer_name="pysc2-labv2",
                   output_aer=False)
    sim_time = 0
    sim_frame_time = .25

    for i in range(5):
        identifier = f'REMUS100_{i}'
        lat, lon = gen_random_pos()
        print(f'Generated random pos: {lat}, {lon}')
        gym.add_platform(identifier, "DELTA_REMUS100_PLATFORM", (lat, lon, -10))

        platform_names = gym.sim.get_platforms()
        for platform_name in platform_names:

            platform = gym.sim.get_platform_by_name(platform_name)
            lla = platform.get_location_lla()
            print(f"Platform: {platform}.  position {lla}")

            mover = platform.get_mover()
            if mover is not None:
                mover.set_heading(0.02)
                mover.go_to_speed(gym.sim.get_sim_time(), 100.0, 100.0, keep_route=False)

    sim_time += sim_frame_time
    for i in range(100):
        for id, plat in gym.get_platforms().items():
            components = plat.get_components()
            pos = plat.get_location_lla()
            print(f"{plat.get_name()}: {pos}")
            if "REMUS" in plat.get_type():
                plat.get_processor("nn_controller").set_aux_double("lastThrust", 1)
                plat.get_processor("nn_controller").set_aux_double("lastRotation", .75)
                # plat.get_processor("nn_controller").set_aux_double("lastThrust", np.random.uniform(0, 1))
                # plat.get_processor("nn_controller").set_aux_double("lastRotation", np.random.uniform(0, 1))
        # print( f'step {i}')
        sim_time += sim_frame_time
        gym.advance_time(sim_time)
        print("Sim time: ", gym.sim.get_sim_time())


if __name__ == "__main__":
    main()
