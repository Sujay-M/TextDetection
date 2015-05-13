clc;clear all;
MAX_AREA = 10000;
MIN_AREA = 50;
X = []
Y = []
for i=1:19
    pathIn = strcat('../new/',int2str(i),'.jpg');
    pathOut = strcat('../new/',int2str(i),'.png');
    colorImage = imread(pathIn);
    mask = logical(imread(pathOut));
    grayImage = rgb2gray(colorImage);
    mserRegions = detectMSERFeatures(grayImage,'RegionAreaRange',[MIN_AREA MAX_AREA]);
    mserRegionsPixels = vertcat(cell2mat(mserRegions.PixelList));
    mserMask = false(size(grayImage));
    ind = sub2ind(size(mserMask), mserRegionsPixels(:,2), mserRegionsPixels(:,1));
    mserMask(ind) = true;
    newMask = mserAnalysis(mserMask,grayImage);
    mask = bwareaopen(mask,MIN_AREA);
    CC = bwconncomp(mask,8);
    y1 = ones(CC.NumObjects,1);
    x1 = zeros(CC.NumObjects,4);
    stats = regionprops(CC,'Area','Perimeter','Eccentricity','Solidity');
    for i=1:CC.NumObjects
        x1(i,1) = stats(i).Area;
        x1(i,2) = stats(i).Perimeter;
        x1(i,3) = stats(i).Eccentricity;
        x1(i,4) = stats(i).Solidity;
    end
    newMask = newMask-mask;
    newMask = bwareaopen(newMask,MIN_AREA);
    CC = bwconncomp(newMask,8);
    y0 = zeros(CC.NumObjects,1);
    x0 = zeros(CC.NumObjects,4);
    stats = regionprops(CC,'Area','Perimeter','Eccentricity','Solidity');
    for i=1:CC.NumObjects
        x0(i,1) = stats(i).Area;
        x0(i,2) = stats(i).Perimeter;
        x0(i,3) = stats(i).Eccentricity;
        x0(i,4) = stats(i).Solidity;
    end
    X = cat(1,X,x0);
    X = cat(1,X,x1);
    Y = cat(1,Y,y0);
    Y = cat(1,Y,y1);
    
end
