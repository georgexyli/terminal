import random
import math
import warnings
from sys import maxsize
import json
import gamelib


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write("Random seed: {}".format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write("Configuring your custom algo strategy...")
        self.config = config

        """
        making the WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR variables
        """
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        if game_state.turn_number == 0:
            game_state = self.initBase(game_state)
        game_state = self.fixBase(game_state)
        game_state = self.addUpgradeTurrets(game_state)
        game_state.submit_turn()

    def fixBase(self, game_state: gamelib.GameState):
        ####potential upgrade --> if there you can't rebuild whole base try to fill the things in the middle
        game_state.attempt_spawn(WALL, wall_locations)
        game_state.attempt_spawn(TURRET, turret_locations)
        return game_state

    def addUpgradeTurrets(self, game_state: gamelib.GameState):
        upgrade_turret_locations = [
            [3, 12],
            [4, 11],
            [7, 9],
            [8, 8],
            [22, 10],
            [23, 11],
            [24, 12],
        ]
        game_state.attempt_upgrade(upgrade_turret_locations)
        game_state.attempt_spawn(TURRET, upgrade_turret_locations)

    def upgradeWalls(self, game_state: gamelib.GameState):
        upgrade_wall_locations = [
            [2, 13],
            [3, 13],
            [4, 12],
            [23, 12],
            [24, 13],
            [25, 13],
        ]
        game_state.attempt_upgrade(upgrade_wall_locations)
        return game_state

    def on_action_frame(self, action_frame_game_state):
        """
        After each deploy phase, the game engine will run the action phase of the round.
        The action phase is made up of a sequence of distinct frames.
        Each of these frames is sent to the algo in order.
        They can be handled in this function.
        """
        ###maybe try to store what attack they are using....

    def initBase(self, game_state: gamelib.GameState):
        global wall_locations, turret_locations
        wall_locations = [
            [2, 13],
            [3, 13],
            [4, 12],
            [5, 11],
            [7, 11],
            [7, 10],
            [8, 9],
            [9, 8],
            [10, 7],
            [11, 6],
            [12, 5],
            [13, 5],
            [14, 5],
            [15, 5],
            [16, 5],
            [17, 5],
            [18, 6],
            [19, 7],
            [20, 8],
            [20, 9],
            [21, 10],
            [22, 11],
            [23, 12],
            [24, 13],
            [25, 13],
        ]
        turret_locations = [[3, 12], [24, 12]]
        game_state.attempt_spawn(WALL, wall_locations)
        game_state.attempt_spawn(TURRET, turret_locations)
        return game_state


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
