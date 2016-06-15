"""

For data augment.

Read all pickle.gz, and plot original image and the noise one.

According to my code about GenerateSubjPickle.py, for a pickle, the first one is 
the original one.


Label of NC:    0
Label of AD:    1
Label of EMCI:  2
Label of LMCI:  3
Label of SMC:   4

@Zhewei
6/15/2016 
"""

import sys,os
import datetime
import gzip
import pickle as Pickle
import numpy as np
from random import shuffle, randint
from PersonIndependent_LSTM import stackData
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
import matplotlib.pyplot as pyplot


totalNo = 55
NoiseNo = 5

index = [i for i in range(totalNo)]
shuffle(index)
DataIndex = index


def main(args):
    if len(args) < 2:
        usage( args[0] )
        pass
    else:
        work( args[1:] )
        pass
    pass

def usage (programm):
    print ("usage: %s ..data/*Subj*.pickle.gz"%(programm))
    
def work(fnames):
    #after shuffle we can just choose the first subject. 
    f = gzip.open(fnames[DataIndex[0]],'rb')
    wholeData,wholeLabel = Pickle.load(f)
    
    print (wholeData.shape)
    sampleNo = wholeData.shape[0]
    timeStep = wholeData.shape[1]
    featureNo = wholeData.shape[2]
    
    
    cycle = sampleNo/(NoiseNo+1)
    print (cycle)
    # find original one and noise one
    originIndex = 0
    noiseIndex = originIndex+cycle
    
    '''
    Draw
    '''
    pyplot.figure(1)
    
    for t in range(timeStep):
        tmp = wholeData[originIndex, ]
        tmp = tmp.reshape(timeStep, featureNo)
        color = 'm'
        plotORI, = pyplot.plot(range(featureNo), tmp[t,:], 'o-', color = color, label = 'Original', alpha = 0.7)
    
    for t in range(timeStep):
        tmp = wholeData[noiseIndex, ]
        tmp = tmp.reshape(timeStep, featureNo)
        color = '#bc82bd'
        plotNOI, = pyplot.plot(range(featureNo), tmp[t,:], 'o-', color = color, label = 'Noise', alpha = 0.7)
    
    pyplot.legend(handles=[plotORI, plotNOI], loc = 4)
    pyplot.show()
    
    
    
    









if __name__ == '__main__':
    main(sys.argv)
    pass