"""
LSTM for data analysis after feature selection.

1. Read pickle.gz in.
2. Separate as train, validation, test
3. We have 214 persons. We totally processed 180 fMRI images. Separate the persons as train, vali, test, and then collect all images belongs to corresponding group.
4. Change the percentage a little bit. Make sure have enough validation data and test data.


Zhewei @ 9/26/2016

"""

import os, gzip
import pickle as Pickle
from random import shuffle
import math
import numpy

from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.initializations import normal, identity


Train_percentage = 0.6
Valid_percentage = 0.2
Groups = 2

class _EachSubject:
    # each subject is a element of a list
    def __init__(self, SubjectID, Sex, DX_Group, imageID):
        self.Sex = Sex
        self.DX_Group = DX_Group
        self.SubjectID = SubjectID
        # baseline is a dict, imageID:data
        self.baseline = {imageID:list()}
        # otherdata after baseline is also a dict, imageID:data
        self.other = {}

def collect_Baseline_And_Other(validDataList):
    Label = list()
    Data = list()
    ID = list()
    for validData in validDataList:
        tmp_list = list(validData.baseline.keys())
        for key in tmp_list:
            try:
                if validData.baseline[str(key)].any():
                    Label.append(validData.DX_Group)
                    Data.append(validData.baseline[str(key)])
                    ID.append(str(key))
                '''if str(key) == '228872':# test at here
                    print (validData.baseline[str(key)])'''
            except AttributeError:
                pass
        if validData.other != {}:
            tmp_list = list(validData.other.keys())
            for other_key in tmp_list:
                try:
                    if validData.other[str(other_key)].any():
                        Label.append(validData.DX_Group)
                        Data.append(validData.other[str(other_key)])
                        ID.append(str(other_key))
                except AttributeError:
                    pass
    return Label, Data, ID

def collect_Baseline_Only(validDataList):
    Label = list()
    Data = list()
    ID = list()
    for validData in validDataList:
        tmp_list = list(validData.baseline.keys())
        for key in tmp_list:
            try:
                if validData.baseline[str(key)].any():
                    Label.append(validData.DX_Group)
                    Data.append(validData.baseline[str(key)])
                    ID.append(str(key))
                '''if str(key) == '228872':# test at here
                    print (validData.baseline[str(key)])'''
            except AttributeError:
                pass
    return Label, Data, ID

def data_to_3D(dataList):
    featureNo = dataList[0].shape[1]
    timeFrame = dataList[0].shape[0]
    # stack data
    Data = numpy.zeros([1,1])
    for dataNo, data in enumerate(dataList):
        if dataNo == 0:
            Data = data
        else:
            Data = numpy.vstack((Data, data))
    return Data.reshape((-1, timeFrame, featureNo))

def label_to_binary(labelList):
    Label = list()
    for label in labelList:
        if label == 'Normal':
            Label.append(0)
        if label == 'AD':
            Label.append(1)
    return Label

os.chdir("/home/medialab/Zhewei/data")
Raw_data = gzip.open('Feature_Selection.pickle.gz', 'rb')
Subjects_data = Pickle.load(Raw_data)

# Now data are in the list Subjects_data.
print ('Totally we have', len(Subjects_data), 'subjects.')
shuffle(Subjects_data)

trainNo = math.floor(len(Subjects_data)*Train_percentage)
validNo = math.floor(len(Subjects_data)*Valid_percentage)

train_Subjects = Subjects_data[0:trainNo]
valid_Subjects = Subjects_data[trainNo:trainNo+validNo]
test_Subjects = Subjects_data[trainNo+validNo:]

print ('We have', len(train_Subjects), 'train subjects.')
print ('We have', len(valid_Subjects), 'valid subjects.')
print ('We have', len(test_Subjects), 'test subjects.')

trainLabel, trainData, trainID = collect_Baseline_And_Other(train_Subjects)
validLabel, validData, validID = collect_Baseline_Only(valid_Subjects)
testLabel, testData, testID = collect_Baseline_Only(test_Subjects)

print ('We have', len(trainID), 'train images.')
print ('We have', len(validID), 'valid images.')
print ('We have', len(testID), 'test images.')
# label, data, ID = collect_Baseline_And_Other(Subjects_data)
# print (len(ID))

# transfer data to 3D
# print (trainData[10])
trainData = data_to_3D(trainData)
validData = data_to_3D(validData)
testData = data_to_3D(testData)
# print (testData.shape)
# print (trainData[10,:,:])

# labels to 0 and 1
trainLabel = label_to_binary(trainLabel)
validLabel = label_to_binary(validLabel)
testLabel = label_to_binary(testLabel)
# print (trainLabel)
# print (validLabel)
# print (testLabel)



"""
LSTM
"""

nb_classes = Groups
timesteps = trainData.shape[1]
featureNo = trainData.shape[2]

Y_train = np_utils.to_categorical(trainLabel, nb_classes)
Y_test = np_utils.to_categorical(testLabel, nb_classes)
Y_valid = np_utils.to_categorical(validationLabel, nb_classes)