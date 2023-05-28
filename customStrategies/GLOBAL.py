WALL = SUPPORT = TURRET = SCOUT = DEMOLISHER = INTERCEPTOR = None
MP = 1
SP = 0

def initGlobal(config):
    global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR
    WALL = config["unitInformation"][0]["shorthand"]
    SUPPORT = config["unitInformation"][1]["shorthand"]
    TURRET = config["unitInformation"][2]["shorthand"]
    SCOUT = config["unitInformation"][3]["shorthand"]
    DEMOLISHER = config["unitInformation"][4]["shorthand"]
    INTERCEPTOR = config["unitInformation"][5]["shorthand"]
