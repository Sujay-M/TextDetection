function [newMask] =  mserAnalysis(mser,img)
    [r,c] = size(img);
    se = strel('square',3);
    mser = imclose(mser,se);
    % imshow(mser);
    % pause();
	CC = bwconncomp(mser);
	stats = regionprops(CC,'BoundingBox','PixelIdxList');
    newMask = false(size(img));
	for i=1:CC.NumObjects
		x1 = stats(i).BoundingBox(1);
   		y1 = stats(i).BoundingBox(2);
    	x2 = x1+stats(i).BoundingBox(3);
    	y2 = y1+stats(i).BoundingBox(4);
        y1(y1==.5)=1;
        x1(x1==.5)=1;
        y2(y2>r) = r;
        x2(x2>c) = c;
    	temp = img(floor(y1):ceil(y2),floor(x1):ceil(x2));
        mu = mean(img(stats(i).PixelIdxList));
        otsu = graythresh(temp);
        mask = false(size(img));
        mask(stats(i).PixelIdxList) = true;
        th = im2bw(temp,otsu);
        if otsu<(mu/255)
            mask(floor(y1):ceil(y2),floor(x1):ceil(x2)) = th&mask(floor(y1):ceil(y2),floor(x1):ceil(x2));
        else
            mask(floor(y1):ceil(y2),floor(x1):ceil(x2)) = not(th)&mask(floor(y1):ceil(y2),floor(x1):ceil(x2));
        end
        newMask = newMask|mask;       
   	end
end