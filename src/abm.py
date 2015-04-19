'''
Created on Apr 17, 2015

@author: stran_000
'''


width = 50
height = 50
dist_norm = 0

sqrt2 = 2**0.5

SMOOTHNESS = 20
share_amount = 0.125
AGENTS_PER_STEP = 10
residents_per_service = 50

#agent types
COBBDOUGLAS = 0
COGNITIVE = 1
agent_type = COBBDOUGLAS
heterogeneity = False
importance_services_proximity = 1.0
numtests = 20

import random as RD
import scipy as SP
import utility as U

world = None

class World(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        global world, dist_norm
        self.agents = []
        self.services = []
        self.patch_at = {}
        self.time = 0
        world = self
        dist_norm = (width*height)**0.5
        self.setUpEnvironment()
        
        
    def setUpEnvironment(self):
        self.envir = SP.zeros([height, width])
        for y in range(height):
            for x in range(width):
                self.envir[y, x] = RD.random()
        
        #diffuse
        for i in range(SMOOTHNESS):
            xs = RD.sample(range(width), width)
            ys = RD.sample(range(height), height)
            for x in xs:
                for y in ys:
                    share = self.envir[y, x]*share_amount
                    share /= 9.0
                    self.envir[y,x] *= (1-share_amount)
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            sharex = (x+dx) % width
                            sharey = (y+dy) % height
                            self.envir[sharey, sharex] += share
                            
        for y in range(height):
            for x in range(width):
                patch = Patch(x, y, self.envir[y,x])
                self.patch_at[(x,y)] = patch
                            
        cx = int(width/2)
        cy = int(height/2)
        first_service = Service(cx, cy)
        self.locateService(first_service)
        
    def step(self):
        self.time += 1
        self.placeAgents()
        self.placeService()
        
    def placeAgents(self):
        for i in range(AGENTS_PER_STEP):
            new_resident = Agent()
            self.locateResident(new_resident)
            self.last_agent = new_resident
            
    def placeService(self):
        if len(self.agents) % residents_per_service == 0:
            new_service = Service(self.last_agent.x, self.last_agent.y)
            self.locateService(new_service)
            
    def locateResident(self, resident):
        x = resident.x
        y = resident.y
        self.patch_at[(x,y)].agents_here.append(resident)
        self.degradeQuality(x,y)
        self.agents.append(resident)
        
    def locateService(self, service):
        x = service.x
        y = service.y
        self.patch_at[(x,y)].services_here.append(service)
        self.degradeQuality(x,y)
        self.services.append(service)
            
    def degradeQuality(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx*dy != 0:
                    mult = 0.9
                elif dx+dy == 0:
                    mult = 0.75
                else :
                    mult = 0.81
                if 0 <= x+dx < width and 0 <= y+dy < height:
                    self.patch_at[(x+dx,y+dy)].quality *= mult
                    self.envir[y+dy,x+dx] *= mult
                    
    def isEmptyAt(self, x, y):
        return (not self.patch_at[(x,y)].agents_here) and (not self.patch_at[(x,y)].services_here)
    
    def findClosestServiceTo(self, x, y):
        return max(self.services, key = lambda srv : (srv.x - x)**2 + (srv.y - y)**2)

class Patch(object):
    
    def __init__(self, x, y, q):
        self.x = x
        self.y = y
        self.quality = q
        self.agents_here = []
        self.services_here = []
        
class Agent(object):
    
    def __init__(self):
#         self.x = RD.randint(0, width-1)
#         self.y = RD.randint(0, height-1)
        if heterogeneity:
            self.alpha_srv = U.GenBoundedRandomNormal(importance_services_proximity, 0.5, 0, 2)
        else:
            self.alpha_srv = importance_services_proximity
        self.alpha_qua = 2 - self.alpha_srv
        if agent_type == COBBDOUGLAS:
            self.CobbDouglasChoice()
            
    def CobbDouglasChoice(self):
        choices = {}  # a dictionary of candidate patches, with utility as value
        for i in range(numtests):
            x = RD.randint(0, width-1)
            y = RD.randint(0, height-1)
            patch = world.patch_at[(x,y)]
            if world.isEmptyAt(x,y):
                srv = world.findClosestServiceTo(x,y)
                dist = ((srv.x-x)**2 + (srv.y-y)**2)**0.5/dist_norm
                qual = world.patch_at[(x,y)].quality
                util = (1/dist)**self.alpha_srv + qual**self.alpha_qua
                choices[patch] = util
        choice = max(list(choices.keys()), key = lambda loc : choices[loc])
        self.x = choice.x
        self.y = choice.y
                
        
class Service(object):
    
    def __init__(self, x = int(width/2), y = int(height/2)):
        self.x = x
        self.y = y
        
import simgui        
if __name__ == '__main__':
    sim = simgui.SimGUI()
    sim.run()