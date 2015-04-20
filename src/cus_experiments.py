'''
Created on Apr 20, 2015

@author: stran_000
'''
import abm
import datetime as DT
import utility as U
import experiment as exp
import collections
from copy import deepcopy

setters = []
setters.append(abm.setAgentType)
setters.append(abm.setHeterogeneity)
setters.append(abm.setServicesImportance)

class CUSExperiment(exp.Experiment):
     
    def __init__(self, setterValues, job_reps = 1, exp_name = "Unnamed", comments = ""):
        super().__init__()
        self.sim = None
        self.setterValues = setterValues
        self.job_repetitions = job_reps
        self.time = 0
        self.Name = exp_name
        self.comments = comments
        
    def setupExperiment(self):
        for setter in setters:
            self.addParameter(setter, self.setterValues[setter])

    def initiateSim(self):
        self.sim = abm.World()
        self.time = 0
    
    def stepSim(self):
        self.time += 1
        self.sim.step()        
    
    def stopSim(self):
        return self.time > 100
    
    def setupSimFuncs(self):
        self.simInitFunc = self.initiateSim 
        self.simStepFunc = self.stepSim
        self.simStopFunc = self.stopSim     
    
    def setupOutputs(self):
        #######################################################################
        """
        Section 4 - Add getter methods, names, and string formats so the automater
        can retrieve and record metrics from your simulation.
        
        #template
        self.addOutput(getterFunction, output_name, output_format)
        
        #Example:
        self.addOutput(getAveragePopulation, "Avg Pop.", "%8.4f")
        # getAveragePopulation() returns the average population of the sim run,
        # and the header "Avg Pop." will be written to the file
        """
        self.addOutput(abm.calculatePacking, "packing", "%1.4f")
        self.addOutput(abm.calculateQualityReduction, "reduction", "%1.4f")



if __name__ == '__main__':
    reps = 30
    exp_name = "CUSExperiment_Main"
    comments = "Sweep across services proximity importance"
    values = {}
    values[abm.setAgentType] = [abm.COBBDOUGLAS, abm.COGNITIVE]
    values[abm.setHeterogeneity] = [False]
    values[abm.setServicesImportance] = [0.2*i for i in range(11)]
    CUSExperiment(values, reps, exp_name, comments).run()        