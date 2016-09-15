%% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%
%
%
%
%
%
%% input image IDs
% clear all
IID = [238623, 303069, 240811, 304790, 371994, 243902, ...
       322442, 286519, 361612, 287493, 361431, 254581, ...
       273218, 290923, 335999, 391150, 257271, 340048, ...
       395105, 274579, 297353, 259654, 299159, 346113, ...
       274825, 397604, 259806, 260580, 277135, 398533, ...
       301757, 346801, 395980, 265132, 336212, 289846, ...
       265125, 289854, 336216, 389367, 268914, 311257, ...
       268917, 349326, 405706, 349320, 286461, 286464, ...
       311258, 279468, 279472, 319634, 319632, 362889, ...
       298515, 298510, 281881, 326301, 361294, 281887, ...
       303083, 326298, 363620, 337404, 283913, ...
       350450, 319211, 238540, 253525, 238542, ...
       296769, 352724, 375151, 296863, 369618, 340743, ...
       368950, 300088, 314505, 368923, 343935, 308182, ...
       262078, 320519, 296612, 268925, 401398, 321439, ...
       297183, 266634, 315798, 296891, 399633, 272223, ...
       327813, 354839, 301492, 403913, 273503, 296638, ...
       316619, 409002, 353130, 269279, 306127, 347150, ...
       401663, 288745, 315850, 355339, 338813, 383452, ...
       300743, 370595, 261918, 246871, 234917, 371750, ...
       305150, 270397, 251325, 255986, 391167, 274090, ...
       337977, 292605, 280365, 302555, 321203, 282646, ...
       362235, 303248, 414942, 325233, 290815, 337993, ...
       309727, 366388, 289559, 366944, 310188, 289656, ...
       387091, 334140, 350835, 348304, 350735, 353800, ...
       266208, 310240, 289588, 350046, 398573, 267713, ...
       346744, 399995, 302615, 285316, 365086, 264214, ...
       330165, 285011, 401073, 279084, 336199, 308403, ...
       308418];

Path = './data/Normal_data/fMRI_%d.txt';
Path2 = './data/Normal_data/DifferentSample.txt';


%===========parameters at here================

% number of slices is the slices in one scan, by mri_info *.nii we can get
% for fMRI it is 64*64*48, so each slice is 64*64, and 48 slices.
ST_Nslices = 48;
ST_TR = 3;
ST_TA = 3-3/48;
ST_SO = [1:1:48];
ST_Refslice = 24;
ST_prefix = '';


% realign & unwarp
RU_pmscan = '';
RU_quality = 0.9;
RU_sep = 4;
RU_fwhm = 5;
RU_rtm = 0;
RU_einterp = 2;
RU_ewrap = [0,0,0];
RU_weight = '';
RU_basfcn = [12,12];
RU_regorder = 1;
RU_lambda = 100000;
RU_jm = 0;
RU_fot = [4,5];
RU_sot = [];
RU_uwfwhm = 4;
RU_rem = 1;
RU_noi = 5;
RU_expround = 'Average';
RU_uwwhich = [2,1];
RU_rinterp = 4;
RU_wrap = [0,0,0];
RU_mask = 1;
RU_prefix = '';

% coregistration
CO_ref = {'/home/medialab/spm12/atlas/AAL2.nii,1'};
CO_cost_fun = 'nmi';
CO_sep = [4,2];
CO_tol = [0.0200,0.0200,0.0200, 1.0000e-03, 1.0000e-03, 1.000e-03, 
        0.0100, 0.0100, 0.0100, 1.0000e-03, 1.0000e-03, 1.000e-03];


CO_fwhm = [7,7];
CO_interp = 4;
CO_wrap = [0,0,0];
CO_mask = 0;
CO_prefix = '';

%=============================================

[~,numfiles] = size(IID);
data = cell(1, numfiles);

for ifile = 1:numfiles
    fileID = IID(ifile);
    IIDfilename = sprintf(Path, fileID);
    
    data{ifile} = importdata(IIDfilename);    
end

% some modification to fit SPM12
% ================================

for ifile = 1:numfiles
    [rows, col] = size(data{1,ifile});
    for irow = 1:rows
        data{1,ifile}{irow,col} = strcat(data{1,ifile}{irow,col},',1');
    end
end


% start to work automatically
fileWrite = fopen(Path2,'w');

for ifile = 1:numfiles
    
    img_data = sort([data{1,ifile}]);
    img_data = img_data(11:140);
    display('Slice Timing..........................................')
    % build the job structure of slice timing
    job.scans = {img_data};
    job.nslices = ST_Nslices;
    job.tr = ST_TR;
    job.ta = ST_TA;
    job.so = ST_SO;
    job.refslice = ST_Refslice;
    job.prefix = ST_prefix;
    % ========================different samples====================
    P = cell(size(job.scans));
    for i = 1:numel(job.scans)
        P{i} = char(job.scans{i});
    end
    Vin     = spm_vol(P{1}(1,:));
    nslices = Vin(1).dim(3);
    if nslices ~= numel(job.so)
        fprintf(fileWrite,'%d\n',IID(ifile));
        fprintf(fileWrite,'%d\n',nslices);
        continue
    end
    % ==============================================================
    
    spm_run_st(job);
    clearvars job;
    display('Realign & Unwarp..........................................')
    job.data.scans = img_data;
    job.data.pmscan = RU_pmscan;
    job.eoptions.quality = RU_quality;
    job.eoptions.sep = RU_sep;
    job.eoptions.fwhm = RU_fwhm;
    job.eoptions.rtm = RU_rtm;
    job.eoptions.einterp = RU_einterp;
    job.eoptions.ewrap = RU_ewrap;
    job.eoptions.weight = RU_weight;
    job.uweoptions.basfcn = RU_basfcn;
    job.uweoptions.regorder = RU_regorder;
    job.uweoptions.lambda = RU_lambda;
    job.uweoptions.jm = RU_jm;
    job.uweoptions.fot = RU_fot;
    job.uweoptions.sot = RU_sot;
    job.uweoptions.uwfwhm = RU_uwfwhm;
    job.uweoptions.rem = RU_rem;
    job.uweoptions.noi = RU_noi;
    job.uweoptions.expround = RU_expround;
    job.uwroptions.uwwhich = RU_uwwhich;
    job.uwroptions.rinterp = RU_rinterp;
    job.uwroptions.wrap = RU_wrap;
    job.uwroptions.mask = RU_mask;
    job.uwroptions.prefix = RU_prefix;
    spm_run_realignunwarp(job);
    clearvars job;
    display('Coregistration..........................................')
    job.ref = CO_ref;
    job.source = img_data(1);
    job.other = img_data(2:end);
    job.eoptions.cost_fun = CO_cost_fun;
    job.eoptions.sep = CO_sep;
    job.eoptions.tol = CO_tol;
    job.eoptions.fwhm = CO_fwhm;
    job.roptions.interp = CO_interp;
    job.roptions.wrap = CO_wrap;
    job.roptions.mask = CO_mask;
    job.roptions.prefix = CO_prefix;
    spm_run_coreg(job);
    
    
end