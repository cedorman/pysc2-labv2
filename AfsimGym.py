import afsim
import sys, os, copy

from afsim.standard_application import StandardApplication, SimType
from afsim.scenario import Scenario
from afsim import EventStepSimulation, draw, GeoPoint, Platform, Mover, Route, Waypoint, Input

'''
Super poorly named class from back when 

NOTE: this was originally located in delta-phase2/ main repo directory 
'''
class AfsimGym:
    def __init__( self, scenario_file: str, aer_name: str = "scenario_output.aer", output_aer=False, disable_stdout=True ):
        StandardApplication.DISABLE_AFSIM_STDOUT = disable_stdout
        with open( scenario_file ) as f:
            scenario_str = f.read()

        self.app = StandardApplication()
        self.scenario = Scenario(self.app)

        self.scenario.load_from_string( scenario_str )
        self.scenario.complete_load()

        if output_aer:
            self.scenario._process_input(f"event_pipe file {aer_name} use_preset full end_event_pipe")
            # self.scenario.set_aer_path(aer_name)

        self.sim = self.app.create_simulation(scenario=self.scenario)
        # self.sim = self.app.create_simulation(scenario=self.scenario, simulation_type=SimType.FRAME_STEPPED)
        self.app.initialize_simulation(self.sim)
        self.sim.start()

    def advance_time( self, until_time ):
        if self.sim.is_active():
            self.sim.advance_time( until_time, True )

    def add_platform( self, platform_name, platform_type, position ):
        new_plat = self.sim.create_platform(platform_type)
        new_plat.set_name( platform_name )

        lat = position[0]
        lat_hem = "n"
        lon = position[1]
        lon_hem = "e"

        if position[0] < 0:
            lat = position[0] * -1
            lat_hem = 's'
        if position[1] < 0:
            lon = position[1] * -1
            lon_hem = 'w'

        route = Route()
        wp = Waypoint(lat=position[0], lon=position[1], alt=position[2], speed=0)
        route.append( wp )
        mover = new_plat.get_mover()

        # new_plat.set_location_lla( lat=position[0], lon=position[1], alt=position[2] )
        input = Input(f"position {lat}{lat_hem} {lon}{lon_hem}")
        new_plat.process_input(input)

        if mover:
            new_plat.get_mover().set_route( self.sim.get_sim_time(), route )
        
        self.sim.add_platform( platform=new_plat )
        return new_plat

    def remove_platform( self, platform_name ):
        # print( f"***** REMOVE PLATFORM {platform_name}" )
        self.sim.delete_platform( sim_time=self.sim.get_sim_time(), platform=platform_name )

    def is_active( self ):
        return self.sim.is_active()

    def terminate( self ):
        # TODO - Determine if this or request_reset is the better option
        self.sim.request_termination()

    def get_platforms( self ):
        return self.sim.get_platforms()