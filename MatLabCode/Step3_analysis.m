%%
% 05/27/2016
%
%

% clear all

%%

%%
IID = [238623 303069 240811 304790 371994 ...\
243902 322442 223896 286519 ...\
361612 233437 287493 361431 254581 ...\
273218 290923 335999 391150 257271 ...\
274579 297353 340048 395105 ...\
259654 274825 299159 346113 397604 ...\
259806 260580 277135 301757 346801 ...\
398533 395980 249406 249407 265125 ...\
265132 289854 289846 336212 336216 ...\
389367 268914 268917 286464 286461 ...\
311258 311257 349326 349320 405706 ...\
279472 279468 298510 298515 319632 ...\
319634 362889 281887 281881 303081 ...\
303083 326301 326298 361294 ...\
310441 337404 363620 283913 319211 ...\
350450 373523 238542 238540 253525 ...\
424849 312870 336708 365243 ...\
297689 313953 377213 368889 296769 ...\
314141 352724 375151 296863 ...\
369618 340743 368950 300088 314505 ...\
343935 368923 308182 262078 296612 ...\
320519 268925 297183 321439 348187 ...\
401398 266634 296891 315798 348166 ...\
399633 272223 301492 327813 ...\
354839 403913 273503 296638 316619 ...\
353130 409002 269279 288745 306127 ...\
347150 401663 315850 338813 355339 ...\
383452 229146 246871 261918 300743 ...\
370595 234917 251325 270397 305150 ...\
371750 255986 274090 292605 337977 ...\
391167 280365 302555 321203 282646 ...\
303248 325233 362235 414942 290815 ...\
309727 337993 366388 289559 310188 ...\
341918 366944 289656 387091 334140 ...\
322060 350835 316542 348304 350735 ...\
317121 353800 266208 289588 310240 ...\
350046 398573 267713 285316 302615 ...\
346744 399995 365086 264214 285011 ...\
330165 401073 279084 336199 308403 ...\
308418 ];

path_ToFile = './data/NC_data/fMRI_%d.txt';
path_ToResult = '/home/medialab/Zhewei/MatLabCode/data/NC_data/NC_Result%d.txt';


lenthOfFMRI = 130;


%% index of AAL2
[index, Label, value] = textread('/home/medialab/spm12/atlas/aal2.nii.txt','%u %s %u');
% then make a dictionary
[i_index,~] = size(index);
dictionary = zeros(i_index, 2);% map index and value
dictionary(:,1) = index;
dictionary(:,2) = value;


%%
[~,numfiles] = size(IID);
data = cell(1, numfiles);

for iifile = 1:numfiles
    fileID = IID(iifile);
    IIDfilename = sprintf(path_ToFile, fileID);

    IID_data = importdata(IIDfilename);
    IID_data = sort(IID_data);
    IID_data = IID_data(11:140);

    data{iifile} = IID_data;
end

%% find global min and global max
global_min = [];
global_max = [];
for ifile = 1:numfiles
    display(ifile);
    for ii = 1:lenthOfFMRI
        frame = data{1,ifile}{ii,1};
        nii_fMRI = load_untouch_nii(frame);
        img = double(nii_fMRI.img);
        local_min = min(min(min(img)));
        local_max = max(max(max(img)));
        global_min = [local_min global_min];
        global_max = [local_max global_max];
    end

end

global_min = min(min(global_min));
global_max = max(max(global_max));
% global_min = -1055;
% global_max = 5032;

%% iterate on fMRI

% open a file, write data in it


parfor ifile = 1:numfiles
    
    IIDfilename = sprintf(path_ToResult, IID(ifile));
    fileWrite = fopen(IIDfilename,'w');


    fprintf(fileWrite,'===========%d================\n',IID(ifile));
    display(ifile);

    nii_atlas = load_untouch_nii('/home/medialab/spm12/atlas/AAL2.nii');% atlas
    [x,y,z] = size(nii_atlas.img);

    for ii = 1:lenthOfFMRI
        frame = data{1,ifile}{ii,1};
        % # Should sort at here
        fid = fopen(frame);
        fprintf(fileWrite,'========================%d===============\n',ii+10);
        display(ii)


        nii_fMRI = load_untouch_nii(frame);% fMRI images

        % empty table, index, sum of intensities, and #of intensities, average
        % value

        statist_table = zeros(i_index, 4);

        % iterate
        %

        test = [];
        for i = 1:x
            for j = 1:y
                for k = 1:z
                    index_intensity = find(nii_atlas.img(i,j,k)==dictionary(:,2));
                    if ~isempty(index_intensity)
                        statist_table(index_intensity,3) = statist_table(index_intensity,3)+1;
                        pixel = (double(nii_fMRI.img(i,j,k))-global_min)/(global_max-global_min);
                        statist_table(index_intensity,2) = statist_table(index_intensity,2)+pixel;
                    end
                end
            end
        end

        for i = 1:i_index
            if statist_table(i,3)~=0
                statist_table(i,4) = statist_table(i,2)/statist_table(i,3);
            end
        end


        fprintf(fileWrite,'%8f\r\n',statist_table(:,4));

    end


end
