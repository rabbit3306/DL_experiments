"""
7/24/2016 start:

This program used to generate general pickle files from the raw data from MatLab.

This time we change the strategy: store the data in a data structure: a dict, and then

save the whole data as a pickle file.

Classes and frames and Label: 

'EMOTION'       176         0
'GAMBLING'      253
'LANGUAGE'      316
'MOTOR'         284
'RELATIONAL'    232         1
'SOCIAL'        274
'WM'            405


1. all data read or write in ./data/HCP_data/

2. data structure: the whole data is a dict.

        keys are subjects, values are a dict, keys are classes, each class results are in a array, 120(zones)*timeframes.
3. We'd better use the residual values. 
4. length. What should we do about different length? Now just simply choose the shortest one.

******************************************

******************************************

Usage:  

Output: an array with the 3D shape SampleNo*FrameNo*FeatureNo and label for each sample

@Zhewei


"""

import sys,os
import gzip
import pickle as Pickle
import numpy as np
import random
import math
from collections import defaultdict
import matplotlib.pyplot as pyplot


#******************************
#******************************
IID_List = (100307,103515,103818,111312,114924, \
117122, 118932, 119833, 120212, 125525, 128632, 130013, \
131621, 137128, 138231, 142828, 143325, 144226, 149337, \
150423, 153429, 156637, 159239, 161731, 162329, 167743, \
172332, 182739, 191437, 192439, 192540, 194140, 197550, \
199150, 199251, 200614, 201111, 210617, 217429, 249947, \
250427, 255639, 304020, 307127, 329440, 355542, 499566, \
530635, 559053, 585862, 611231, 638049, 665254, 672756, \
685058, 729557, 732243, 792564, 826353, 856766, 859671, \
861456, 865363, 877168, 889579, 894673, 896778, 896879, \
901139, 917255, 937160 )


WholeData = defaultdict(dict)
WholeRes = defaultdict(dict)

postfix = '.pickle.gz'
#******************************
ZoneNo = 120
MagicNoSub = 6 # for subject
MagicNoClassBegin = 7
MagicNoClassEnd = 9
global_max = 48728
global_min = -6619

#******************************


def main(args):
    if len(args) < 2:
        usage( args[0] )
        pass
    else:
        dataAnalysis( args[1:] )
        pass
    pass
    
def usage (programm):
    print ("usage: %s ../data/HCP_data/*.txt"%(programm))
    
def Renormalize(className, value):
    # className = 'EM', 'GA', 'LA', 'MO', 'RE', 'SO', 'WM'
    if className == 'EM':
        local_max = 47784
        local_min = -5402
    if className == 'RE':
        local_max = 48728
        local_min = -6619
    # go back to the original value
    value = value*(local_max-local_min)+local_min
    # renormalize
    value = (value-global_min)/(global_max-global_min)
    return value

def origin_Or_res(datalist, option=None):
    data = np.array(datalist)
    data = data.reshape(ZoneNo,-1)
    if option == 'res':
        timeStep = np.shape(data)[-1]
        tmpData = np.zeros((ZoneNo, timeStep-1))
        for time in range(1, timeStep):
            tmpData[:,time-1] = data[:,time]-data[:,time-1]
        data = tmpData
    return data
            
    
def work(files):
    # can return wholedata or whole residual data
    invalidSubj = list()
    for fNo, fi in enumerate(files):
        #print (fi)
        tmpFile = os.path.basename(fi)
        Subj = str(tmpFile[0:MagicNoSub])
        Class = str(tmpFile[MagicNoClassBegin:MagicNoClassEnd])
        with open(fi) as f:
            content = f.readlines()
            
        tmpData = list()

        for line in content:
            try:
                tmp = float(line)
                # renormalize
                tmp = Renormalize(Class, tmp)
                tmpData.append(tmp)
                if math.isnan(tmp):
                    invalidSubj.append(Subj+Class)
            except ValueError:
                pass
        # save the class value in a dict
        WholeData[Subj][Class] = origin_Or_res(tmpData)
        WholeRes[Subj][Class] = origin_Or_res(tmpData,option='res')
        
    print ('The subjects that contain NaN valuse are :',set(invalidSubj))
    # print(len(WholeRes['100307']['RE']))
    return WholeRes
    

def visualize(data):

    # a lot of dirty work at here.
    Data = data
    timeStep1 = np.shape(Data['100307']['EM'])[-1]
    timeStep2 = np.shape(Data['100307']['RE'])[-1]
    sampleNo = len(list(Data.keys()))
    No1 = 0
    No2 = 0
    pyplot.figure(1)
    for IID in list(Data.keys()):

        # print (IID)
        if 'EM' in list(Data[IID].keys()):
            for time1 in range(ZoneNo):
                color = (No1/(2*sampleNo)+0.5,0,0)
                plot1, = pyplot.plot(range(timeStep1), Data[IID]['EM'][time1,:], 'o-', color = color, label = 'EM', alpha = 0.7)
            No1 += 1
        if 'RE' in list(Data[IID].keys()):
            for time1 in range(ZoneNo):
                color = (0,No2/(2*sampleNo)+0.5,0)
                plot2, = pyplot.plot(range(timeStep2), Data[IID]['RE'][time1,:], 'o-', color = color, label = 'RE', alpha = 0.7)
            No2 += 1
            
    pyplot.legend(handles=[plot1, plot2], loc = 4)   
    pyplot.show()

def dataAnalysis(files):
    Data = work(files)
    # visualize
    # visualize(Data)
    
    # Now lets's do RNN
    






















if __name__ == "__main__":
    main( sys.argv )
    pass
