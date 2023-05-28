####Function to initize the base
import GLOBAL
import gamelib

wall_locations=[[1,13]]
turret_locations=[[0,13]]

def initBase(game_state: gamelib.GameState):
    game_state.attempt_spawn(GLOBAL.WALL, wall_locations)

    game_state.attempt_spawn(GLOBAL.TURRET, turret_locations)
    return game_state
