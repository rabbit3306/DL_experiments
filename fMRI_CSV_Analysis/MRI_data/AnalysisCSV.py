"""
If in one scan we have MPRAGE or MP-RAGE, choose one of them (the one show itself later in .csv)

"""


import csv


class _EachSubject:
    # each subject is a element of a list
    def __init__(self, SubjectID, DX_Group, MRI_imageID):
        self.DX_Group = DX_Group
        self.SubjectID = SubjectID
        # baseline 
        self.MRI_baseline = {MRI_imageID: list()}
        # otherdata after baseline 
        self.MRI_other = list()

wholeDataofCSV = list()
with open ('idaSearch_5_24_2017.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        wholeDataofCSV.append(row)

print (wholeDataofCSV[0])
print (wholeDataofCSV[2])

subject_list = list()
description_list = list()

for i in wholeDataofCSV:
    if i['DX Group'] == 'AD' or i['DX Group'] == 'Normal':
        if i['Description'] == 'MPRAGE' or i['Description'] == 'MP-RAGE' \
               or i['Description'] == 'MP RAGE':
            subject_list.append(i['Subject ID'])
            description_list.append(i['Description'])

print (list(set(description_list)))
print (len(list(set(subject_list))))



"""
Subject_ID = None
group_list = list()

for row in wholeDataofCSV:
    if row['Subject ID'] == '027_S_0461':
        print (row['DX Group'])
    if Subject_ID != row['Subject ID']:
        # end of a subject
        Subject_ID = row['Subject ID']
        DX_group = row['DX Group']
        group_list.append(DX_group)
    if Subject_ID == row['Subject ID']:
        
        if row['DX Group'] != DX_group:
            print ('ERROR: The GX group changed.')
        group_list.append(DX_group)

print (list(set(group_list)))
                    

print (a)
"""


# For MoCo series
MRI_ImageID = None
Subject_ID = None
Baseline_flag = False # False means no baseline exist
DX_group = None
iAge = 0
ValidData = list()
_Subject = None

for row in wholeDataofCSV:
    if Subject_ID != row['Subject ID']:
        # end of a subject
        if MRI_ImageID != None:
            if Baseline_flag == False:
                # False means no baseline exist
                _Subject = _EachSubject(Subject_ID, DX_group, MRI_ImageID)
                Baseline_flag = True
            else:
                _Subject.MRI_other.append(MRI_ImageID)
        if _Subject != None:
            ValidData.append(_Subject)
        MRI_ImageID = None
        fMRI_ImageID = None
        if row['Description'] == 'MPRAGE' or row['Description'] == 'MP-RAGE' \
           or row['Description'] == 'MP RAGE':
            MRI_ImageID = row['Image ID']
        Subject_ID = row['Subject ID']
        iAge = row['Age']
        DX_group = row['DX Group']
        Baseline_flag = False
        _Subject = None

    if Subject_ID == row['Subject ID']:
        # same subject
        if row['Age'] != iAge:
            # end of a scan
            if MRI_ImageID != None:
                if Baseline_flag == False:
                    # False means no baseline exist
                    _Subject = _EachSubject(Subject_ID, DX_group, MRI_ImageID)
                    Baseline_flag = True
                else:
                    if row['DX Group'] != DX_group:
                        print ('ERROR: The GX group changed.')
                    _Subject.MRI_other.append(MRI_ImageID)
            MRI_ImageID = None
            if row['Description'] == 'MPRAGE' or row['Description'] == 'MP-RAGE' \
               or row['Description'] == 'MP RAGE':
                MRI_ImageID = row['Image ID']
                if row['DX Group'] != DX_group:
                    print ('ERROR: The GX group changed.')
            iAge = row['Age']
        else:
            # during a scan
            if row['Description'] == 'MPRAGE' or row['Description'] == 'MP-RAGE' \
               or row['Description'] == 'MP RAGE':
                MRI_ImageID = row['Image ID']
                if row['DX Group'] != DX_group:
                    print ('ERROR: The GX group changed.')

print (len(ValidData))
# print the MRI IDs
MRI_list = list()
MRI_baselineList = list()
Subjects_in_group = list()

with open('Original_MRI_ImageID_2','w') as f:
    for subject in ValidData:
        if subject.DX_Group == "AD" or subject.DX_Group == "Normal":
            Subjects_in_group.append(subject.SubjectID)
            if subject.MRI_baseline != None:
                #print (subject.MRI_baseline.keys())
                #print (list(subject.MRI_baseline.keys()))
                MRI_list.append(str(list(subject.MRI_baseline.keys())[0]))
                MRI_baselineList.append(str(list(subject.MRI_baseline.keys())[0]))
                f.write(str(list(subject.MRI_baseline.keys())[0]))
                f.write(',')
            if subject.MRI_other:
                for ID in subject.MRI_other:
                    if ID != None:
                        MRI_list.append(ID)
                        f.write(ID)
                        f.write(',')

print('We have', len(Subjects_in_group), 'subjects.')
print('MRI Image:', len(MRI_list))
print('MRI Baseline:', len(MRI_baselineList))

with open('Original_MRI_ImageID', 'r') as f:
    old_MRI_ID = f.read().split(',')

print (len(old_MRI_ID))
print (old_MRI_ID[0])
