import cv2
import numpy as np
'''
Stroke Width Transform as proposed in,
Detecting Text in Natural Scenes with Stroke Width Transform by,
Boris Epshtein, Eyal Ofek and Yonatan Wexler

It takes edge image and gradient direction as the input and gives the stroke width transform.
Starting from an edge it tries to find the opposite edge which constitutes for a stroke. The length is then assigned 
to the intermediate points as the stroke width.

Not yet complete, special cases like corners are not implemented. 
After obtaining the stroke widths, apply connected components with a criteria that adjacent points with little variation 
in the stroke lengths are of the same component. (In opencv floodFill will do the job)
'''
def swtEpshtein(edge_im,grad_angle,maxLength=50):
	'Takes edge image(canny) and gradient direction to give the stroke width transform'
	height,width = edge_im.shape
	swt = np.zeros(edge_im.shape, np.uint16)
	for i in range(height):
		for j in range(width):
			if edge_im.item(i,j)!=0:
				points = [(i,j)]
				for l in range(maxLength):
					length = l+1					
					x1 = j + length*math.cos(grad_angle.item(i,j))
					y1 = i + length*math.sin(grad_angle.item(i,j))
					if x1>=width or y1>=height or x1<0 or y1<0:
						break
					if edge_im.item(y1,x1)!=0:
						if abs(grad_angle.item(i,j)-grad_angle.item(y1,x1))<0.52:
							points.append((y1,x1))
							for point in points:
								if swt.item(point[0],point[1])==0 or swt.item(point[0],point[1])>length:
									swt.itemset(point[0],point[1],length)
								
					else:
						points.append((y1,x1))
	return swt

'''
Stroke width Transform proposed in,
ROBUST TEXT DETECTION IN NATURAL IMAGES WITH EDGE-ENHANCED MAXIMALLY STABLE EXTREMAL REGIONS by,
Huizhong Chen, Sam S. Tsai, Georg Schroth, David M. Chen, Radek Grzeszczuk  and Bernd Girod

This is a very good approximation of the stroke width transform originally proposed by Epshtein et al.
Here it takes a binary image and applies the distance transform to it. The maximum value in the 
neighbourhood (1/2 of strokewidth) is assigned to all the pixels.
Algorithm as proposed in the paper.
'''

def swtChen(img):
	'takes a binary image and gives swt'
	dT = cv2.distanceTransform(img,cv2.DIST_L2,5)
	dT = np.uint8(np.absolute(dT))
	_,dist_threshold = cv2.threshold(dT,1,255,cv2.THRESH_BINARY)
	diff = img - dist_threshold
	dist = dT.copy()
	dist[diff==255] = 1
	
	lookUp = {}
	height,width = dist.shape
	for i in range(height):
		for j in range(width):
			if dist.item(i,j)>0:
				pval = dist.item(i,j)
				xlist = [j-1,j,j+1]
				ylist = [i-1,i,i+1]
				points = []
				for y in ylist:
					if (y>0 and y<height):
						for x in xlist:
							if (x>0 and x<width):
								if dist.item(y,x)<pval:
									points.append((y,x))
				lookUp[(i,j)] = points
	min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(dist)
	stroke = max_val
	swt = dist.copy()
	while stroke>0:
		Index = np.where(dist==stroke)
		Index = np.transpose(Index)
		strokeIndex = map(tuple,Index) 
		NeighbourIndex = []
		for point in strokeIndex:
			NeighbourIndex = NeighbourIndex+lookUp[point]
		while NeighbourIndex:
			i = 0
			swt.itemset(NeighbourIndex[i],stroke)
			for point in NeighbourIndex:
				NeighbourIndex = NeighbourIndex+lookUp[point]
			NeighbourIndex.remove(NeighbourIndex[i])
		stroke = stroke-1																																							
	return swt

'''
My above implementation of Chen et al. algorithm is very inefficient. It takes forever to perform the operations
because of all those memory fetches and huge dictionaries.
I altered the algorithm a bit, it works very fast comparitively, so not sure if its the same:p
'''
def swtChenAltered(img):
	'takes distance transform and gives swt'
	dT = cv2.distanceTransform(img,cv2.DIST_L2,5)
	dT = np.uint8(np.absolute(dT))
	_,dist_threshold = cv2.threshold(dT,1,255,cv2.THRESH_BINARY)
	diff = img - dist_threshold
	dist = dT.copy()
	dist[diff==255] = 1
	lookUp = {}
	height,width = dist.shape
	for i in range(height):
		for j in range(width):
			if dist.item(i,j)>0:
				xlist = [j-1,j,j+1]
				ylist = [i-1,i,i+1]
				point = (i,j)
				for y in ylist:
					if (y>0 and y<height):
						for x in xlist:
							if (x>0 and x<width):
								if dist.item(y,x)>dist.item(point):
									point = (y,x)
				lookUp[(i,j)] = point
	swt = dist.copy()
	for i in range(height):
		for j in range(width):
			if dist.item(i,j)>0:
				point = (i,j)
				while point != lookUp[point]:
					point = lookUp[point]
				val = swt.item(point)
				swt.itemset(i,j,val)
	return swt
