import cv2
import numpy as np
import sys
import swt
#from matplotlib import pyplot as plt

'''
Grow edges function is used to prune the mser so that the connected letters will be separated.
We ll have to supply the canny edges and gradient direction, function returns grown edges.
The below function is still incomplete, and an approximation to this function is used in the below implementation.
I have used morphological geadient operator(ie. dilation(img)-erosion(img)), it gives the approximate edgesgrown.
'''
def growEdges(edgeMser_im,grad_angle,maxLength=1):
	'takes an edge and gradient direction and gives an edge grown image'
	if DarkonLight==1:
		grad_angle = -grad_angle
	edgeGrown = edgeMser_im.copy()
	for i in range(height):
		for j in range(width):
			if edgeMser_im.item(i,j)!=0:
				x1 = j
				y1 = i
				for l in range(maxLength):
					length = l+1
					x1 = j + length*math.cos(grad_angle.item(y1,x1))
					y1 = i + length*math.sin(grad_angle.item(y1,x1))
					if x1>=width or y1>=height or x1<0 or y1<0:
						break
					edgeGrown.itemset(y1,x1,255)
	return edgeGrown

'''
Below function is used for connected components analysis, it removes all the components which doesn't satisfy 
the criteria used.(area,aspect ratio,solidity and eccentricity)
'''
def CCAnalysis(CC,no,stats):
	finalMask = np.zeros((height,width),np.uint8)	
	mask = np.zeros((height,width),np.uint8)
	for i in range(1,no):
		mask[::] = 0
		mask[CC==i] = 255
		image, contours, hierarchy = cv2.findContours(mask.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		area = stats.item(i,4)
		aspectRatio = stats.item(i,2)/stats.item(i,3)
		if area>MAX_AREA or area<MIN_AREA:
			continue		
		if aspectRatio>MAX_ASPECT_RATIO:
			continue		
		convex_hull = cv2.convexHull(contours[0])
		convex_area = cv2.contourArea(convex_hull)
		if convex_area!=0:
			solidity = area/float(convex_area)
		else:
			solidity = 0
		if solidity<MIN_SOLIDITY:
			continue
		ellipse = cv2.fitEllipse(contours[0])
		(center,axes,orientation) = ellipse
		majoraxis_length = max(axes)
		minoraxis_length = min(axes)
		eccentricity = np.sqrt(1-(minoraxis_length/majoraxis_length)**2)
		if eccentricity>MIN_ECCENTRICITY:
			continue
		finalMask = finalMask|mask
	return finalMask

'''
Simple Display function
'''
def display(img,winName='img'):
	"Display function"
	winHeight = height
	winWidth = width
	ratio = float(winHeight)/winWidth
	if winHeight>MAX_HEIGHT:
		winHeight = MAX_HEIGHT
		winWidth = int(winHeight/ratio)
	if winWidth>MAX_WIDTH:
		winWidth = MAX_WIDTH
		winHeight = int(winWidth*ratio)
	cv2.namedWindow(winName)
	cv2.imshow(winName,cv2.resize(img,(winWidth,winHeight)))
	cv2.waitKey(0)
	cv2.destroyAllWindows()

'''
Main function that returns the regions of interest(text)
'''
def detectText(img):
	mser = cv2.MSER_create()
	regions = mser.detectRegions(img, None)
	mask = np.zeros(img.shape, np.uint8)
	for points in regions:
		for point in points:
			mask.itemset(point[1],point[0],255)
	'''
	smoothedInput = cv2.GaussianBlur(img, (7,7), math.sqrt(2))
	edges = cv2.Canny(smoothedInput, 120, 120)
	MserAndCanny = mask&edges

	sobelx = cv2.Sobel(img,cv2.CV_64F,1,0)
	sobely = cv2.Sobel(img,cv2.CV_64F,0,1)
	gradAngle = cv2.phase(sobelx,sobely)
	MserAndCannyGrown = growEdges(MserAndCanny,gradAngle,2)
	MserAndCannyGrown = np.uint8(np.absolute(MserAndCannyGrown))
	'''
	se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
	gradient = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, se)
	edgeEnhancedMserMask = (255 - gradient)&mask
	#display(edgeEnhancedMserMask)
	no,CC,stats,Cen = cv2.connectedComponentsWithStats(edgeEnhancedMserMask)
	new = CCAnalysis(CC,no,stats)
	#display(new)
	strokeWidths = swt.swtChenAltered(new)
	strokeWidths = np.uint8(np.absolute(strokeWidths))
	#plt.imshow(strokeWidths, cmap='jet', interpolation='nearest');plt.show()
	newer = np.zeros((height,width),np.uint8)
	mask = np.zeros((height,width),np.uint8)
	no,CC,stats,Cen = cv2.connectedComponentsWithStats(new)
	for i in range(1,no):
		mask[::] = 0
		Index = np.where(CC==i)
		mask[Index] = 255
		if np.std(strokeWidths[Index])/np.mean(strokeWidths[Index])>0.35:
			continue
		newer = newer|mask
	se1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(50,50))
	se2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
	im1 = cv2.morphologyEx(newer, cv2.MORPH_CLOSE, se1)
	im2 = cv2.morphologyEx(im1, cv2.MORPH_OPEN, se2)
	return im2	

if __name__ == '__main__':
	try: path = sys.argv[1]		
	except: path = './DataSet/text.png'
	try: DarkonLight = int(sys.argv[2])
	except: DarkonLight = 1
	img = cv2.imread(path,0)
	if img is None:
		print 'Failed to load image file:', path
		sys.exit(1)

	height,width = img.shape
	MAX_AREA = 10000
	MIN_AREA = 50
	MAX_ASPECT_RATIO = 2
	MIN_SOLIDITY = .4
	MIN_ECCENTRICITY = .995
	MAX_WIDTH = 1280
	MAX_HEIGHT = 720
	display(img)	
	detected = detectText(img)
	display(detected)