function [ swt ] = swtChenAltered( img )
    distanceImage    = bwdist(~img);
    distanceImage = uint8(distanceImage);
    im = im2bw(distanceImage,1/255);
    dif = img - im;
    distanceImage(dif>0) = 1;
    [r,c] = size(img);
    lookUp = zeros(r,c,2);
    temp = [-1 0 1];
    for i=1:r
    	for j=1:c
    		if distanceImage(i,j)>0
                x = j+temp;
                y = i+temp;
    			a = 0+(x>0&x<c);
                b = 0+(y>0&y<r)';
                A = b*a;
                [x,y] = ind2sub(size(A),find(A==1));
                x = x+(i-2);
                y = y+(j-2);
                max=0;
                pos = [i,j];
                for k=1:size(x,1)
                    if distanceImage(x(k),y(k))>max
                        max=distanceImage(x(k),y(k));
                        pos=[y(k),x(k)];
                    end
                end
                lookUp(i,j,1) = pos(1);
                lookUp(i,j,2) = pos(2);
            end
        end
    end    
	swt = distanceImage;
	for i=1:r
    	for j=1:c
    		if distanceImage(i,j)>0
    			point = [i,j];
    			while (point(1) ~= lookUp(point(1),point(2),1) && point(2) ~= lookUp(point(1),point(2),2))
					y = lookUp(point(1),point(2),1);
                    x = lookUp(point(1),point(2),2);
                    point = [y,x];
                end
				swt(i,j) = swt(point(1),point(2));
            end
        end
	end
end

