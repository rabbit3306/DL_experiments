clear all;

% fileFold = fullfile('~/data/Weizmann_Seg/Labels/Origin/');
% postFix = '*.png';
% cd ~/data/Weizmann_Seg/Labels/Origin/
% path = '~/data/Weizmann_Seg/Labels/BW/';
% 
% dirInput = dir(fullfile(fileFold, postFix));
% fileNames = {dirInput.name};
% 
% [m,n] = size(fileNames);
% for files = 1:n
%     I  = imread(fileNames{1,files});
%     [m_I, n_I, ~] = size(I);
%     tmp_img = zeros(m_I,n_I);
%     for i=1:m_I
%         for j = 1:n_I
%             if I(i,j,1) == 255 && I(i,j,2) == 0 && I(i,j,3) == 0
%                 tmp_img(i,j) = 1;
%             end
%         end
%     end
%     saveName = strcat(path,fileNames{1,files});
%     imwrite(tmp_img, saveName);
%     
% end



fileFold = fullfile('~/data/Weizmann_Seg/Img_BW/Origin/');
postFix = '*.png';
cd ~/data/Weizmann_Seg/Img_BW/Origin/
path = '~/data/Weizmann_Seg/Img_BW/50_50/';
sizeTo = 50;

dirInput = dir(fullfile(fileFold, postFix));
fileNames = {dirInput.name};

[m,n] = size(fileNames);
for files = 1:n
    I  = imread(fileNames{1,files});
    I = rgb2gray(I);
    new_file=strrep(fileNames{1,files}, '.png', '.jpg');
    I_500 = imresize(I, [sizeTo sizeTo]);
    saveName = strcat(path,new_file);
    imwrite(I_500, saveName);
    
end