'''
Created on Apr 17, 2015

@author: stran_000
'''

import matplotlib
matplotlib.use('TkAgg')

import pylab as PL
import pycxsimulator
import abm
import random as RD

import matplotlib.pyplot as plt


class SimGUI(object):
    '''
    classdocs
    '''


    def __init__(self, psetters = None):
        self.funcs = [self.reset, self.draw, self.step]
        self.env_map = plt.get_cmap("YlGn")
        self.ag_map = plt.get_cmap("binary")
        self.srv_map = plt.get_cmap("Reds")
        self.psetters = psetters
        
    def reset(self):
        self.world = abm.World()
        self.time = 0
        self.packing = 0
            
    def step(self):
        self.time += 1
        self.world.step()
        if self.time %10 == 0:
            print("Average quality is %f"%abm.calculateQuality())
        
    def draw(self):
        PL.cla()
        PL.pcolor(self.world.envir, cmap = self.env_map, vmin = 0, vmax = 1)
        PL.axis('image')
        PL.hold(True)
        
        #plot agents
        x = [ag.x + 0.5 for ag in self.world.agents]
        y = [ag.y + 0.5 for ag in self.world.agents]
        s = [1 for ag in self.world.agents]
        PL.scatter(x, y, c = s, cmap = self.ag_map)
        
        #plot services
        x = [srv.x + 0.5 for srv in self.world.services]
        y = [srv.y + 0.5 for srv in self.world.services]
        s = [0.5 for srv in self.world.services]
        PL.scatter(x, y, c = s, cmap = self.srv_map, vmin = 0, vmax = 1)
        
        PL.hold(False)
        time_string = 't = ' + str(self.time)
        if self.time % 5 == 1:
            self.packing = abm.calculatePacking()
        pack_string = ", \t packing:  " + str(self.packing)
        PL.title(time_string + pack_string)
        
    def run(self):
        if self.psetters:
            pycxsimulator.GUI(parameterSetters = self.psetters).start(func=self.funcs)
        else:
            pycxsimulator.GUI().start(func=self.funcs)
        
if __name__ == '__main__':
    sim = SimGUI()
    sim.run()
    