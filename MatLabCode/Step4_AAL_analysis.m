%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%   1. Step4. After After_SPM.m
%   2. Now the fMRI files are all matched with AAL template, we need to
%       separate fMRI files as 120 zones as AAL.
%   3. How to do it faster other than travel all the pixels? Separate AAL 
%       template as 120 matrix, and for each matrix its corresponding zone is 
%       1 and others are 0. Then do pointwise multiplication.
%
%
%
%
%
%

fMRI_IID = [346237];

Path_fMRI = './data/AD_data/fMRI_SPM_%d.txt';
addpath(genpath('Tools/NIfTI_Tools/'));
%% index of AAL2
frame_No = 130;
zones_No = 120;
[index, Label, value] = textread('/home/medialab/spm12/atlas/aal2.nii.txt','%u %s %u');
% then make a dictionary
[i_index,~] = size(index);
dictionary = zeros(i_index, 2);% map index and value
dictionary(:,1) = index;
dictionary(:,2) = value;

AAL_nii = load_nii('/home/medialab/spm12/atlas/AAL2.nii');
AAL_matrices = cell(1, zones_No); % 120 zones
AAL_PixelNO = zeros(1, zones_No); % How many pixels for each zone?
for iMatrix = 1:zones_No
    aal_matrix = AAL_nii.img;
    aal_matrix(aal_matrix ~= dictionary(iMatrix,2)) = 0;
    aal_matrix(aal_matrix == dictionary(iMatrix,2)) = 1;
    % How many pixels for each zone?
    AAL_PixelNO(iMatrix) = sum(sum(sum(aal_matrix)));
    AAL_matrices{iMatrix} = double(aal_matrix);
end

[~,numfiles] = size(fMRI_IID);
fMRI_data = cell(1, numfiles);

for ifile = 1:numfiles
    fileID = fMRI_IID(ifile);
    IIDfilename = sprintf(Path_fMRI, fileID);
    fMRI_data{ifile} = sort(importdata(IIDfilename));
end

for ifile = 1:numfiles
    display(ifile);
    feature = zeros(zones_No, frame_No);
    for jframe = 1:frame_No
        fMRI_nii = load_nii(fMRI_data{ifile}{jframe});
        img = double(fMRI_nii.img);
        img_max = max(max(max(img)));
        img = img/img_max;
        for kzone = 1:zones_No
            feature(kzone, jframe) = sum(sum(sum(img.*AAL_matrices{kzone})))/AAL_PixelNO(kzone);
        end
    end
    
    % save in .mat files
    mat_name = strcat(num2str(fMRI_IID(ifile)), '.mat');
    save(feature, mat_name);
end
    