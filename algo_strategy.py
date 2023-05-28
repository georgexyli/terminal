import random
import math
import warnings
from sys import maxsize
import json
from customStrategies import *

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config

        """
        making the WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR variables
        """
        initGlobal(config)

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        if game_state.turn_number == 1:
            game_state = initBase(game_state)
        game_state.submit_turn()


    def on_action_frame(self, action_frame_game_state):
        """
        After each deploy phase, the game engine will run the action phase of the round.
        The action phase is made up of a sequence of distinct frames. 
        Each of these frames is sent to the algo in order. 
        They can be handled in this function. 
        """
        ###maybe try to store what attack they are using....


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
