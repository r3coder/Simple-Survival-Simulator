
import pygame as pg
import numpy as np

import random

from game_util import *
from config import *


area_w = CONFIG_AREA_W
area_h = CONFIG_AREA_W

area_resource = np.zeros((area_w,area_h),dtype=int)
instances = list()

global_turn = 0
global_player_idx = 0

cell_w = CONFIG_CELL_W
cell_h = CONFIG_CELL_H

class instance():
    def __init__(self, idx, initx, inity, controller = -1):
        self.idx = idx
        self.x = initx
        self.y = inity
        
        self.hp = CONFIG_HP_INITIAL
        self.hp_max = CONFIG_HP_MAX
        self.hp_decay_mode = CONFIG_HP_DECAY_MODE
        self.hp_decay_value = CONFIG_HP_DECAY_VALUE

        self.dmg_base = CONFIG_DMG_BASE
        self.dmg_coef_hp = CONFIG_DMG_COEF_HP
        self.dmg_coef_reflect = CONFIG_DMG_COEF_REFLECT
        
        self.state_reserved = STATE_IDLE
        
        self.controller = controller # negative value for manual controll
        self.print_message("CREATED",1)
        self.print_info(mode = 0)
    
    def __del__(self):
        self.print_message("DELETED",1)

    def is_alive(self):
        return True if self.hp > 0 else False


    def print_info(self, mode = 0):
        if mode == 0:
            print("    idx:%d, Controller:%d"%(self.idx, self.controller))
            print("    hp:%5d/%5d, dmg:%5d,%1.3f,%1.3f"%(self.hp, self.hp_max, self.dmg_base, self.dmg_coef_hp, self.dmg_coef_reflect))

    def print_message(self, msg = "", lv = 0):
        if CONFIG_DEBUG_INSTANCE == 0 or CONFIG_DEBUG_INSTANCE >= lv:
            print("Inst.%d: %s"%(self.idx,msg))

    def execute_turn(self):
        if not self.is_alive():
            return None

        # Move or attack
        isMoveAvailable = True
        isAttack = False
        attackTarget = None
        if   self.state_reserved == STATE_MOVL: target = (self.x-1,self.y  )
        elif self.state_reserved == STATE_MOVR: target = (self.x+1,self.y  )
        elif self.state_reserved == STATE_MOVU: target = (self.x  ,self.y-1)
        elif self.state_reserved == STATE_MOVD: target = (self.x  ,self.y+1)
        else:                                   target = (self.x  ,self.y  )

        # Wall checking
        if target[0] < 0 or target[0] >= area_w or target[1] < 0 or target[1] >= area_h:
            isMoveAvailable = False
            self.print_message("MOVE CANCELLED by WALL", 3)
        # Object colliding
        else:
            for inst in instances:
                if inst.idx != self.idx and (inst.x == target[0] and inst.y == target[1]):
                    isMoveAvailable = False
                    isAttack = True
                    attackTarget = inst
                    self.print_message("MOVE CANCELLED by OBJ", 3)
                    break
        
        # Move to target position
        if isMoveAvailable:
            self.x = target[0]
            self.y = target[1]
        # Attack Enemy
        elif isAttack:
            attackTarget.hp -= int(self.hp*self.dmg_coef_hp)
            self.hp -= int(attackTarget.hp*self.dmg_coef_hp*self.dmg_coef_reflect)
        
        if not self.is_alive():
            return None
        
        # Gain resource
        self.hp+=area_resource[self.x,self.y]
        area_resource[self.x,self.y] = 0
        self.health_check()

        # Decay health
        if self.hp_decay_mode == 0:
            self.hp -= self.hp_decay_value
        self.health_check()

    def health_check(self):
        if self.hp > self.hp_max:
            self.hp = self.hp_max
        elif self.hp <= 0:
            self.hp = 0 # Death
        
def print_debug_main(msg ="", lv = 0):
    if CONFIG_DEBUG_MAIN == 0 or CONFIG_DEBUG_MAIN >= lv:
        print("Main:",msg)

def spawn_resource_basic():
    for x in range(area_w):
        for y in range(area_h):
            if np.random.rand()<CONFIG_RESOURCE_SPAWN_RATE:
                area_resource[x,y] += 1


def game_init():
    if CONFIG_PLAYER_ENABLE:
        inst = instance(global_player_idx, 1, 1)
        instances.append(inst)

    controlidx = 0
    for instanceSpawnCounter in range(CONFIG_INSTANCE_COUNT-len(instances)):
        isSpawnPossible = False
        while (not isSpawnPossible):
            isSpawnPossible = True
            locx = random.randrange(area_w)
            locy = random.randrange(area_h)
            # Check if instance collides
            for inst in instances:
                if inst.x == locx and inst.y == locy:
                    isSpawnPossible = False
                    break
        # Spawn instance
        inst = instance(len(instances), locx, locy, controlidx)
        instances.append(inst)
        controlidx += 1

def execute_turn():  
    # Call global turn as global
    global global_turn, instances, global_player_idx
    print_debug_main("Turn %d: Initiated"%(global_turn),1)

    # Shuffle order
    print_debug_main("Turn %d: Order shuffled"%(global_turn),3)
    order = []
    for i in range(len(instances)):
        order.append(i)
    random.shuffle(order)
    
    # Execute instance turn
    print_debug_main("Turn %d: Execute instance turn"%(global_turn),3)
    for instidx in order:
        instances[instidx].execute_turn()
    
    # Delete instances
    print_debug_main("Turn %d: Instance death"%(global_turn),3)
    instances_new = []
    for inst in instances:
        if inst.hp > 0: instances_new.append(inst)
        else:
            if inst.controller < 0:
                global_player_idx = -1
            del inst
    instances = instances_new

    # Spawn resources
    print_debug_main("Turn %d: Spawn Resources"%(global_turn),3)
    if CONFIG_RESOURCE_SPAWN_METHOD == 0:
        spawn_resource_basic()
    
    # Cap resources
    for x in range(area_w):
        for y in range(area_h):
            if area_resource[x,y] > CONFIG_RESOURCE_MAX:
                area_resource[x,y] = CONFIG_RESOURCE_MAX;
    
    # Increase turn
    global_turn += 1

def assign_state():
    for inst in instances:
        if inst.controller < 0:
            continue
        # put some random actions!
        inst.state_reserved = random.choice([STATE_IDLE, STATE_MOVL, STATE_MOVR, STATE_MOVU, STATE_MOVD])

if __name__ == "__main__":
    print("="*50)
    print("Debug message level")
    if CONFIG_DEBUG_MAIN >= 0:
        print("    Global:", CONFIG_DEBUG_MAIN)
    if CONFIG_DEBUG_INSTANCE >= 0:
        print("    Instance:", CONFIG_DEBUG_INSTANCE)
    print("="*50)
    print_config()
    print("="*50)

    # init pygame
    pg.init()
    
    # define game area
    size = [cell_w*area_w, cell_h*area_h+40]
    scr = pg.display.set_mode(size)

    # set basic fonts
    f_b20 = pg.font.SysFont("comicsansms", 20)
    f_b12 = pg.font.SysFont("comicsansms", 12)

    pg.display.set_caption("Simulation")

    done = False
    clock = pg.time.Clock()
    
    # initialize game
    game_init()

    while not done:
        clock.tick(60)
        turn_passed = False
        # keydown event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                done = True
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                turn_passed = True
            if event.type == pg.KEYDOWN and event.key == pg.K_LEFT: # Temp
                if global_player_idx >= 0:
                    instances[global_player_idx].state_reserved = STATE_MOVL
                turn_passed = True
            if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT: # Temp
                if global_player_idx >= 0:
                    instances[global_player_idx].state_reserved = STATE_MOVR
                turn_passed = True
            if event.type == pg.KEYDOWN and event.key == pg.K_UP: # Temp
                if global_player_idx >= 0:
                    instances[global_player_idx].state_reserved = STATE_MOVU
                turn_passed = True
            if event.type == pg.KEYDOWN and event.key == pg.K_DOWN: # Temp
                if global_player_idx >= 0:
                    instances[global_player_idx].state_reserved = STATE_MOVD
                turn_passed = True
        scr.fill(COL_WHITE)
        text = f_b20.render("Turn:{}".format(global_turn), True, COL_BLACK)
        scr.blit(text, (20,cell_h*area_h+10))
        
        # draw grid
        for xi,line in enumerate(area_resource):
            for yi, elem in enumerate(line):
                pg.draw.polygon(scr, COL_BLACK, get_grid_rectange(xi,yi,0),4)
                text = f_b20.render(str(area_resource[xi,yi]), True, COL_GREEN)
                scr.blit(text, (xi*cell_w+5,yi*cell_h+5))
                
        # draw instances
        for ii, inst in enumerate(instances):
            pg.draw.polygon(scr,COL_RED,get_grid_rectange(inst.x,inst.y,3),3)
            text = f_b12.render(get_state_text(inst.state_reserved), True, COL_BLUE)
            scr.blit(text, (inst.x*cell_w+20,inst.y*cell_h+0))
            text = f_b12.render(str(inst.hp), True, COL_RED)
            scr.blit(text, (inst.x*cell_w+20,inst.y*cell_h+10))
            text = f_b12.render(str(inst.x)+","+str(inst.y), True, COL_RED)
            scr.blit(text, (inst.x*cell_w+20,inst.y*cell_h+20))
            text = f_b12.render(str(inst.controller), True, COL_RED)
            scr.blit(text, (inst.x*cell_w+20,inst.y*cell_h+30))
        
        pg.display.flip()
        
        # handle turn pass
        if turn_passed:
            execute_turn()
            assign_state()
