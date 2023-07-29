import random
import math
import warnings
from sys import maxsize
import json
import gamelib
from queue import Queue
import math


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        self.HORIZONTAL = 1
        self.VERTICAL = 2
        self.MAPSIZE = 27
        self.interceptorLocations = []
        self.game_turn = 0
        self.frame_number = 0
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
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP, CONFIG
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        CONFIG = config
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
        self.frame_number = 0
        i=0
        gamelib.debug_write(self.interceptorLocations)
        while len(self.interceptorLocations)!=0 and self.interceptorLocations[i][2] != self.interceptorLocations[-1][2]:
            i +=1
        if len(self.interceptorLocations) != 0:
            self.interceptorLocations = self.interceptorLocations[i:]
        game_state = gamelib.GameState(self.config, turn_state)
        if game_state.turn_number == 0:
            game_state = self.initBase(game_state)
        game_state = self.fixBase(game_state)
        game_state = self.upgradeWalls(game_state)
        game_state = self.addUpgradeTurrets(game_state)
        game_state = self.spawn_attack(game_state, game_state.game_map)
        game_state.suppress_warnings(True)
        game_state.suppress_warnings(True)
        self.game_turn += 1

        game_state.submit_turn()

    def fixBase(self, game_state: gamelib.GameState):
        ####potential upgrade --> if there you can't rebuild whole base try to fill the things in the middle
        game_state.suppress_warnings(True)
        game_state.attempt_spawn(WALL, wall_locations)
        game_state.attempt_spawn(TURRET, turret_locations)
        return game_state

    def attackCombo():
        return

    ###when to stop saving NEED TO DEBUG
    def savingLimitReached(self, game_state: gamelib.GameState):
        return game_state.get_resource(MP) * 1.25 >= game_state.project_future_MP()

    # returns matrix with distance from start X Y -1 means not yet calculated or infinity
    def BFS_onmap(self, x, y, game_map: gamelib.GameMap):
        queue = Queue()
        queue.put((x, y))
        visted = [[-1] * (self.MAPSIZE + 1) for _ in range((self.MAPSIZE + 1))]
        visted[x][y] = 0
        while not queue.empty():
            a, b = queue.get()
            ##gamelib.debug_write(a,b)
            for i, j in [(a - 1, b), (a + 1, b), (a, b + 1), (a, b - 1)]:
                if game_map.in_arena_bounds([i, j]) and visted[i][j] < 0:
                    if len(game_map[i, j]) == 0:
                        queue.put((i, j))
                        visted[i][j] = visted[a][b] + 1
        return visted

    def next_step(self, game_map: gamelib.GameMap, x, y, last_direction, target_edge):
        visted_s = self.BFS_onmap(x, y, game_map)
        shortest_dis = 777
        for [a, b] in game_map.get_edges()[target_edge]:
            if visted_s[a][b] < shortest_dis and visted_s[a][b] != -1:
                shortest_dis = visted_s[a][b]
        ## if we cannot reach the edge
        if shortest_dis == 777:
            furthest_y = 0
            target_x = -1
            stop_loop = False
            for i in range(self.MAPSIZE, 0, -1):
                if stop_loop:
                    break
                for j in range(1, self.MAPSIZE + 1):
                    if visted_s[j][i] != -1:
                        if target_edge == 0 and j > target_x:
                            target_x = j
                        elif target_edge == 1 and j < target_x:
                            target_x = j
                        furthest_y = i
                        stop_loop = True
            shortest_dis = visted_s[target_x][furthest_y]

            if shortest_dis == 0:
                return -1, -1

            ##use the choosing direction function
            return self.choose_direction(
                shortest_dis,
                x,
                y,
                target_edge,
                last_direction,
                game_map,
                furthest_y,
                target_x,
            )

        ## if we can reach the edge
        else:
            ##use the choose direction function
            return self.choose_direction(
                shortest_dis, x, y, target_edge, last_direction, game_map, -1, -1
            )

    def find_shortest_on_edge(self, game_map, target_edge, visted):
        new_shortest_dis = 777
        for [i, j] in game_map.get_edges()[target_edge]:
            if visted[i][j] < new_shortest_dis and visted[i][j] != -1:
                new_shortest_dis = visted[i][j]
        return new_shortest_dis

    ##NOTE the furthest_y is what helps us see if it is to an edge
    def choose_direction(
        self,
        shortest_dis,
        x,
        y,
        target_edge,
        last_direction,
        game_map,
        furthest_y,
        target_x,
    ):
        step = [
            ((last_direction == self.VERTICAL), (last_direction == self.HORIZONTAL)),
            (
                -1 * (last_direction == self.VERTICAL),
                -1 * (last_direction == self.HORIZONTAL),
            ),
            ((last_direction != self.VERTICAL), (last_direction != self.HORIZONTAL)),
            (
                -1 * (last_direction != self.VERTICAL),
                -1 * (last_direction != self.HORIZONTAL),
            ),
        ]
        for i, j in step:
            i += x
            j += y
            if not game_map.in_arena_bounds([i, j]) or (game_map[i, j] is not None and len(game_map[i, j]) != 0):
                continue
            visted = self.BFS_onmap(i, j, game_map)
            if furthest_y == -1:
                new_shortest_dis = self.find_shortest_on_edge(
                    game_map, target_edge, visted
                )
            else:
                new_shortest_dis = visted[target_x][furthest_y]
            if new_shortest_dis == shortest_dis - 1:
                return i, j
        return -1, -1

    ####when calling function remember to use game_state.copy()
    def mimic_path(
        self,
        unit: gamelib.GameUnit,
        unitsLeft: int,
        game_state: gamelib.GameState,
        game_map: gamelib.GameMap,
        location,
    ):
        x, y = location
        damageToWall = (
            wallDestroyed
        ) = (
            damageToUpgradedWall
        ) = (
            upgradedWallDestroyed
        ) = (
            damageToTurret
        ) = (
            turretDestroyed
        ) = (
            damageToUpgradedTurret
        ) = (
            upgradedTurretsDestroyed
        ) = (
            damageToSupport
        ) = (
            supportDestroyed
        ) = damageToUpgradedSupport = upgradedSupportsDestroyed = damageToEnemyUser = 0
        currentUnitHealth = unit.max_health
        ret = False
        frame = 0
        targetEdge = game_state.get_target_edge([x, y])
        prevMovDir = self.HORIZONTAL
        for i in self.interceptorLocations:
            game_map.add_unit(INTERCEPTOR, [i[0], i[1]], 1)
            game_state.game_map.add_unit(INTERCEPTOR, [i[0],i[1]], 1)
        while True:
            ##update your location if on the edge end while loop and return
            unit.x, unit.y = self.next_step(
                game_map, unit.x, unit.y, prevMovDir, targetEdge
            )
            if x == unit.x:
                prevMovDir = self.VERTICAL
            else:
                prevMovDir = self.HORIZONTAL

            if [unit.x, unit.y] in game_map.get_edges()[targetEdge]:
                damageToEnemyUser += unitsLeft
                ret = True
            ##self destruct
            if unit.x == -1:
                for i in [x - 1, x, x + 1]:
                    for j in [y - 1, y, y + 1]:
                        if not game_map.in_arena_bounds([i, j]):
                            continue
                        if game_map[i, j] is None:
                            continue
                        if len(game_map[i, j]) <= 0:
                            continue
                        if game_map[i, j][0].health <= unit.max_health * unitsLeft:
                            if game_map[i, j][0].unit_type == WALL:
                                if game_map[i, j][0].upgraded == True:
                                    damageToUpgradedWall += game_map[i, j][0].health
                                    upgradedWallDestroyed += 1
                                else:
                                    damageToWall += game_map[i, j][0].health
                                    wallDestroyed += 1
                            elif game_map[i, j][0].unit_type == TURRET:
                                if game_map[i, j][0].upgraded == True:
                                    damageToUpgradedTurret += game_map[i, j][0].health
                                    upgradedTurretsDestroyed += 1
                                else:
                                    damageToTurret += game_map[i, j][0].health
                                    turretDestroyed += 1
                            else:
                                if game_map[i, j][0].upgraded == True:
                                    damageToUpgradedSupport += game_map[i, j][0].health
                                    upgradedSupportDestroyed += 1
                                else:
                                    damageToSupport += game_map[i, j][0].health
                                    supportDestroyed += 1
                        else:
                            if game_map[i, j][0].unit_type == WALL:
                                if game_map[i, j][0].upgraded == True:
                                    damageToUpgradedWall += unit.max_health * unitsLeft
                                else:
                                    damageToWall += unit.max_health * unitsLeft
                            elif game_map[i, j][0].unit_type == TURRET:
                                if game_map[i, j][0].upgraded == True:
                                    damageToUpgradedTurret += (
                                        unit.max_health * unitsLeft
                                    )
                                else:
                                    damageToTurret += unit.max_health * unitsLeft
                            else:
                                if game_map[i, j][0].upgraded == True:
                                    damageToUpgradedSupport += (
                                        unit.max_health * unitsLeft
                                    )
                                else:
                                    damageToSupport += unit.max_health * unitsLeft
                ret = True
            x, y = unit.x, unit.y
            ##turrets attack and change game state
            for attacker in game_state.get_attackers(location, 0):
                currentUnitHealth -= attacker.damage_i
                if currentUnitHealth <= 0:
                    unitsLeft -= 1
                    if unitsLeft <= 0:
                        ret = True
                        break
                    currentUnitHealth = unit.max_health
            if ret == True:
                break

            for i in self.interceptorLocations:
                if game_state.get_target(gamelib.GameUnit(INTERCEPTOR, CONFIG, x=i[0], y=i[1], player_index=1)) is not None:
                    currentUnitHealth -= 20
                    if currentUnitHealth <= 0:
                        unitsLeft -= 1
                        if unitsLeft <= 0:
                            ret = True
                            break
                        currentUnitHealth = unit.max_health
            if ret == True:
                break


            ##unit attack and change game state
            attacksLeft = unitsLeft
            while attacksLeft > 0:
                unitAttacked = game_state.get_target(unit)
                if unitAttacked is None:
                    break
                attackNum = min(
                    math.ceil(unitAttacked.health / unit.damage_i), attacksLeft
                )
                attacksLeft -= attackNum
                game_state.game_map.remove_unit([x, y])
                damageDone = attackNum * unit.damage_i
                unitAttacked.health -= damageDone
                dead = False
                if unitAttacked.health > 0:
                    game_state.game_map[unitAttacked.x, unitAttacked.y][
                        0
                    ] = unitAttacked
                else:
                    if unitAttacked.unit_type == INTERCEPTOR:
                        game_state.game_map[unitAttacked.x,unitAttacked.y].pop()
                    else:
                        game_state.game_map.remove_unit([unitAttacked.x, unitAttacked.y])
                        dead = True
                if unitAttacked.unit_type == TURRET and unitAttacked.upgraded == False:
                    damageToTurret += damageDone
                    if dead:
                        turretDestroyed += 1
                if unitAttacked.unit_type == TURRET and unitAttacked.upgraded == True:
                    damageToUpgradedTurret += damageDone
                    if dead:
                        upgradedTurretsDestroyed += 1
                if unitAttacked.unit_type == WALL and unitAttacked.upgraded == False:
                    damageToWall += damageDone
                    if dead:
                        wallDestroyed += 1
                if unitAttacked.unit_type == WALL and unitAttacked.upgraded == True:
                    damageToUpgradedWall += damageDone
                    if dead:
                        upgradedWallDestroyed += 1
                if unitAttacked.unit_type == SUPPORT and unitAttacked.upgraded == False:
                    damageToSupport += damageDone
                    if dead:
                        supportDestroyed += 1
                if unitAttacked.unit_type == SUPPORT and unitAttacked.upgraded == True:
                    damageToUpgradedSupport += damageDone
                    if dead:
                        upgradedSupportsDestroyed += 1
            frame += 1

        ##check if our dude die and end the while loop or
        return (
            damageToWall,
            wallDestroyed,
            damageToUpgradedWall,
            upgradedWallDestroyed,
            damageToTurret,
            turretDestroyed,
            damageToUpgradedTurret,
            upgradedTurretsDestroyed,
            damageToSupport,
            supportDestroyed,
            damageToUpgradedSupport,
            upgradedSupportsDestroyed,
            damageToEnemyUser,
            x,
            y,
        )

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
        return game_state

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
        return

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
    
    def spawn_attack(self, game_state: gamelib.GameState, game_map: gamelib.GameMap):
        bestscore=500
        bestunit = None
        bestlocation = None
        bestnum = 0
        if self.savingLimitReached(game_state):
            bestscore=0
        for type in [SCOUT, DEMOLISHER]:
            unit = gamelib.GameUnit(type, CONFIG, x=13, y=0, player_index=0)
            spawnable = int(game_state.number_affordable(unit.unit_type))
            if spawnable == 0:
                continue
            for number in range(1, spawnable, math.ceil(spawnable/3)):
                for location in[[16,2], [25,11]]:
                    [unit.x, unit.y] = location
                    damageToWall, wallDestroyed, damageToUpgradedWall, upgradedWallDestroyed, damageToTurret, turretDestroyed, damageToUpgradedTurret, upgradedTurretsDestroyed, damageToSupport, supportDestroyed, damageToUpgradedSupport, upgradedSupportsDestroyed, damageToEnemyUser, x, y = self.mimic_path(unit, number, game_state, game_map, [unit.x, unit.y])
                    score = (damageToWall + 30*wallDestroyed + damageToUpgradedWall + 60*upgradedWallDestroyed +20*damageToTurret + 200*turretDestroyed + damageToUpgradedTurret + 100*upgradedTurretsDestroyed + damageToSupport + 15*supportDestroyed +damageToUpgradedSupport + 30*upgradedSupportsDestroyed + 100*damageToEnemyUser)
                    if score > bestscore:
                        bestscore = score
                        bestunit = unit.unit_type 
                        bestlocation = location
                        bestnum = number
        if bestunit is not None:
            game_state.attempt_spawn(bestunit, bestlocation, num=bestnum)
        return game_state
    
    def on_action_frame(self, string_state: str):
        if self.frame_number % 8 == 0:
            game_state = json.loads(string_state)
            p2Units = game_state["p2Units"]
            for unit in p2Units[5]:
                if unit is not None and unit[1] == 16:
                    self.interceptorLocations.append([unit[0],unit[1], self.game_turn])
        self.frame_number += 1



if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
