'''
Created on Apr 17, 2015

@author: stran_000
'''


width = 75
height = 75
dist_norm = 0

sqrt2 = 2**0.5 + 0.01

SMOOTHNESS = 20
share_amount = 0.125
AGENTS_PER_STEP = 10
residents_per_service = 50

#agent types
COBBDOUGLAS = 0
COGNITIVE = 1
agent_type = COGNITIVE
#agent_type = COBBDOUGLAS
heterogeneity = False
importance_services_proximity = 0.0
numtests = 50

def setAgentType(int_value = agent_type):
    global agent_type
    agent_type = int_value
    return int_value

def setHeterogeneity(bool_value = heterogeneity):
    global heterogeneity
    heterogeneity = bool_value
    return bool_value

def setServicesImportance(float_value = importance_services_proximity):
    global importance_services_proximity
    importance_services_proximity = float_value
    return float_value

def setNumTests(int_value = numtests):
    global numtests
    numtests = int_value
    return int_value

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
        global world, dist_norm, numtests
        self.agents = []
        self.services = []
        self.patch_at = {}
        self.time = 0
        world = self
        dist_norm = (width*height)**0.5
        numtests = int(dist_norm)
        self.setUpEnvironment()
        
        
    def setUpEnvironment(self):
        self.envir = SP.zeros([height, width])
        self.starting_quality = 0
        for y in range(height):
            for x in range(width):
                qual = RD.random()
                self.envir[y, x] = qual
                self.starting_quality += qual
        self.starting_quality /= (width*height)
        
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
        if agent_type == COGNITIVE:
            self.CognitiveChoice()
            
    def CobbDouglasChoice(self):
        choices = {}  # a dictionary of candidate patches, with utility as value
        for i in range(numtests):
            valid_location = False
            while not valid_location:
                x = RD.randint(0, width-1)
                y = RD.randint(0, height-1)
                if world.isEmptyAt(x, y):
                    valid_location = True
            srv = world.findClosestServiceTo(x,y)
            dist = ((srv.x-x)**2 + (srv.y-y)**2)**0.5/dist_norm
            eval_patch = world.patch_at[(x,y)]
            qual = eval_patch.quality
            util = (1/dist)**self.alpha_srv + qual**self.alpha_qua
            choices[eval_patch] = util
        choice = max(list(choices.keys()), key = lambda loc : choices[loc])
        self.x = choice.x
        self.y = choice.y
        
        
    def CognitiveChoice(self):
        self.alpha_qua /= 2
        self.alpha_srv /= 2
        residence_found = False
        evaluations = 0
        residence = None
        best_dist = dist_norm
        best_qual = 0
        srv = RD.choice(world.services)
        dx = 0
        dy = 0
        for i in range(numtests):
            valid_location = False
            tries = 0
            while not valid_location:
                x = RD.randint(0, width-1)
                y = RD.randint(0, height-1)
                if 0<=x<width and 0<=y<height:
                    if world.isEmptyAt(x, y):
                        valid_location = True
#                     srv = world.findClosestServiceTo(x,y)
                    dist = ((srv.x-x)**2 + (srv.y-y)**2)**0.5
            eval_patch = world.patch_at[(x,y)]
            qual = eval_patch.quality            
            if qual > best_qual and dist < best_dist:
                residence = eval_patch
                best_qual = qual
                best_dist = dist
            else:
                if dist < best_dist and qual > self.alpha_qua*best_qual:
                    residence = eval_patch
                    best_dist = dist
                    best_qual = qual
                if qual > best_qual and dist < (1-self.alpha_srv)*best_dist:
                    residence = eval_patch
                    best_qual = qual
                    best_dist = dist
            
#             if 1/dist > self.alpha_srv and qual > self.alpha_qua:
#                 break
                
        self.x = residence.x
        self.y = residence.y
                
        
class Service(object):
    
    def __init__(self, x = int(width/2), y = int(height/2)):
        self.x = x
        self.y = y
        
def calculatePacking():
    num_neighbors = []
    for agent in world.agents:
        x=agent.x
        y=agent.y
        neighbors = 0
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if 0<=x+dx<width and 0<=y+dy<height:
                    neighbors += len(world.patch_at[(x+dx,y+dy)].agents_here)
        neighbors -= 1 # need to decrement where the agent is
        num_neighbors.append(neighbors)
    return U.mean(num_neighbors)/8

def calculateQualityReduction():
    avg_quality = sum(map(sum, world.envir))/(width*height)
    reduction = (world.starting_quality - avg_quality)/world.starting_quality
    return reduction
        
import simgui        
if __name__ == '__main__':
    sim = simgui.SimGUI()
    sim.run()