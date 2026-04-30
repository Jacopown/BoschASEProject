#In this file I define 5 different paths among which the user can decide which one to run 
#NOTE! all paths have a default lenght of 30 seconds


#my car will move in a circular path and then stop 
PATH1 =  [
    ("DESTRA_sustained", 25, 6, 26),
    ("STOP",            -90, 6,  4),
]

#my car will move straight, right, straight and then stop
PATH2 = [
    ("DRITTO_1",      0, 6, 10),
    ("DESTRA",       30, 6,  8),
    ("DRITTO_2",      0, 6,  8),
    ("STOP",        -90, 6,  4),
]

#my car will turn left_sharp, straight,right_sharp and then stop 
PATH3 =  [
    ("SINISTRA_sharp", -50, 6, 9),
    ("DRITTO",           0, 6, 8),
    ("DESTRA_sharp",    50, 6, 9),
    ("STOP",           -90, 6, 4),
]


#my car will move straight,left_slight,right_slight,straight_fast,stop
PATH4 =  [
    ("DRITTO",           0,  6, 7),
    ("SINISTRA_slight", -15,  6, 6),
    ("DESTRA_slight",    15,  6, 6),
    ("DRITTO_fast",       0, 10, 7),
    ("STOP",            -90,  6, 4),
]

#my car will move at zigzag
PATH5 =[
    ("SINISTRA_slight_1", -15, 6, 4),
    ("DESTRA_slight_1",    15, 6, 4),
    ("SINISTRA_slight_2", -15, 6, 4),
    ("DESTRA_slight_2",    15, 6, 4),
    ("SINISTRA_slight_3", -15, 6, 4),
    ("DESTRA_slight_3",    15, 6, 4),
    ("STOP",              -90, 6, 6),
]

PATHS = {
    "PATH1": PATH1,
    "PATH2": PATH2,
    "PATH3": PATH3,
    "PATH4": PATH4,
    "PATH5": PATH5,
}


def get_path(name):
    """Return the path with the given name (e.g. 'PATH1')."""
    if name not in PATHS:
        raise KeyError(f"Unknown path '{name}'. Available: {list(PATHS)}")
    return PATHS[name]


def list_paths():
    """Return the list of all available path names."""
    return list(PATHS.keys())
