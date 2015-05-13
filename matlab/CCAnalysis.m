function [ regionFilteredTextMask ] = CCAnalysis( img )
    connComp = bwconncomp(img);
    stats = regionprops(connComp,'Area','Eccentricity','Solidity');
    regionFilteredTextMask = img;
    regionFilteredTextMask(vertcat(connComp.PixelIdxList{[stats.Eccentricity] > .995})) = 0;
    regionFilteredTextMask(vertcat(connComp.PixelIdxList{[stats.Area] < 150 | [stats.Area] > 2000})) = 0;
    regionFilteredTextMask(vertcat(connComp.PixelIdxList{[stats.Solidity] < .4})) = 0;
end

