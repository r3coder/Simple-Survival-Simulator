
COL_BLACK = (  0,  0,  0)
COL_WHITE = (255,255,255)
COL_BLUE  = (  0,  0,255)
COL_GREEN = (  0,255,  0)
COL_RED   = (255,  0,  0)

STATE_IDLE = 0
STATE_MOVL = 1
STATE_MOVR = 2
STATE_MOVU = 3
STATE_MOVD = 4
# STATE_ATKL = 5
# STATE_ATKR = 6
# STATE_ATKU = 7
# STATE_ATKD = 8

CONFIG_DEBUG_INSTANCE = True

CONFIG_INSTANCE_COUNT = 6
CONFIG_PLAYER_ENABLE = True

CONFIG_HP_MAX = 100
CONFIG_HP_INITIAL = 50
CONFIG_HP_DECAY_MODE = 0 # 0 = Absoulte, 1 = portion
CONFIG_HP_DECAY_VALUE = 1
CONFIG_DMG_BASE = 5
CONFIG_DMG_COEF_HP = 0.1
CONFIG_DMG_COEF_REFLECT = 0.5

CONFIG_AREA_W = 10
CONFIG_AREA_H = 10

CONFIG_CELL_W = 60
CONFIG_CELL_H = 60

CONFIG_RESOURCE_MAX = 10
CONFIG_RESOURCE_SPAWN_METHOD = 0 # 0:Basic Method
CONFIG_RESOURCE_SPAWN_RATE = 0.1

