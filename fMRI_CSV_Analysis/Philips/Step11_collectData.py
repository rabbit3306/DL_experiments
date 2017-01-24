"""
After preprocessing, read .1D data in a data structure which also
contain subjects information.




"""
import os
import pickle
import gzip
import numpy
import glob


class _EachSubject:
    # each subject is a element of a list
    def __init__(self, SubjectID, DX_Group, MRI_imageID, fMRI_imageID):
        self.DX_Group = DX_Group
        self.SubjectID = SubjectID
        # baseline 
        self.MRI_baseline = MRI_imageID
        self.fMRI_baseline = fMRI_imageID
        # otherdata after baseline 
        self.MRI_other = list()
        self.fMRI_other = list()

class _Subject_with_data:
    def __init__(self, SubjectID, DX_Group):
        self.DX_Group = DX_Group
        self.SubjectID = SubjectID
        # baseline 
        self.MRI_baseline = dict()
        self.fMRI_baseline = dict()
        # otherdata after baseline 
        self.MRI_other = list()
        self.fMRI_other = list()

def read_1D_files(imageID):
    signals = numpy.empty([2, 2])
    for zone_no in range(1,121):
        file_name = glob.glob('/home/medialab/data/ADNI/Philips/fMRI/fMRI_'\
                              +imageID+'_*/_t'+str(zone_no)+'.1D')
        with open(file_name[0], 'rb') as f:
            zone_singal = list()
            for i in f.readlines():
                zone_singal.append(str(i)[1:][1:-3])
        if zone_no == 1:
            signals = zone_singal;
        else:
            signals = numpy.concatenate((signals, zone_singal))
    signals = signals.reshape((120,-1))
    return signals

with gzip.open('Clean_imageID.gz', 'rb') as input_file:
    subjects_list = pickle.load(input_file)

print (len(subjects_list))
Subjects_with_data = list()

for subject in subjects_list:
    subject2 = _Subject_with_data(subject.SubjectID, subject.DX_Group)
    if subject.DX_Group == "AD" or subject.DX_Group == "Normal":
        # baseline
        if subject.fMRI_baseline != None:
            print(subject.fMRI_baseline)
            signals = read_1D_files(subject.fMRI_baseline)
            subject2.fMRI_baseline = {subject.fMRI_baseline:signals}
        other_list = list()
        for other_ImageID in subject.fMRI_other:
            if other_ImageID != None:
                signals = read_1D_files(other_ImageID)
                other_list.append({other_ImageID:signals})
        subject2.fMRI_other = other_list

        Subjects_with_data.append(subject2)

print(len(Subjects_with_data))
with gzip.open("Clean_imageID_with_Data.gz", "wb") as output_file:
    pickle.dump(Subjects_with_data, output_file)



