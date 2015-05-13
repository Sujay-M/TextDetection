import cv2
import numpy as np
import sys
import swt

def geometricAnalysis(mask,stat):
	image, contours, hierarchy = cv2.findContours(mask.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	area = stat.item(4)
	aspectRatio = stat.item(2)/stat.item(3)
	if area>MAX_AREA or area<MIN_AREA:
		return False		
	if aspectRatio>MAX_ASPECT_RATIO:
		return False
	if len(contours[0])<5:
		return False		
	convex_hull = cv2.convexHull(contours[0])
	convex_area = cv2.contourArea(convex_hull)
	if convex_area!=0:
		solidity = area/float(convex_area)
	else:
		solidity = 0
	if solidity<MIN_SOLIDITY:
		return False
	ellipse = cv2.fitEllipse(contours[0])
	(center,axes,orientation) = ellipse
	majoraxis_length = max(axes)
	minoraxis_length = min(axes)
	eccentricity = np.sqrt(1-(minoraxis_length/majoraxis_length)**2)
	if eccentricity>MIN_ECCENTRICITY:
		return False
	return True

def CCAnalysis(CC,no,stats):
	finalMask = np.zeros((height,width),np.uint8)	
	mask = np.zeros((height,width),np.uint8)
	for i in range(1,no):
		mask[::] = 0
		mask[CC==i] = 255
		if geometricAnalysis(mask,stats[i,:]):
			finalMask = finalMask|mask
	return finalMask
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
def MserAnalysis(mser,img):
	'Analyzes mser region properties to segment connected regions'
	no,CC,stats,Cen = cv2.connectedComponentsWithStats(mser)
	newMask = np.zeros(mser.shape,np.uint8)
	for i in range(1,no):
		Index = np.where(CC==i)		
		mean = np.mean(img[Index])
		roi = img[stats.item(i,1):stats.item(i,1)+stats.item(i,3),stats.item(i,0):stats.item(i,0)+stats.item(i,2)]
		ret2,th = cv2.threshold(roi,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		if mean>ret2:
			newMask[stats.item(i,1):stats.item(i,1)+stats.item(i,3),stats.item(i,0):stats.item(i,0)+stats.item(i,2)]=th
		else:
			newMask[stats.item(i,1):stats.item(i,1)+stats.item(i,3),stats.item(i,0):stats.item(i,0)+stats.item(i,2)]=cv2.bitwise_not(th)
	return newMask
def detectText(img):
	mser = cv2.MSER_create()
	regions = mser.detectRegions(img, None)
	mask = np.zeros((height,width), np.uint8)
	for points in regions:
		for point in points:
			mask.itemset(point[1],point[0],255)
	display(mask)
	
	edgeEnhancedMserMask = MserAnalysis(mask,img)
	display(edgeEnhancedMserMask)
	no,CC,stats,Cen = cv2.connectedComponentsWithStats(edgeEnhancedMserMask)
	new = CCAnalysis(CC,no,stats)
	display(new)
	strokeWidths = swt.swtChenAltered(new)
	strokeWidths = np.uint8(np.absolute(strokeWidths))
	# plt.imshow(strokeWidths, cmap='jet', interpolation='nearest');plt.show()
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
	# display(newer)
	se1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(50,50))
	se2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
	im1 = cv2.morphologyEx(newer, cv2.MORPH_CLOSE, se1)
	im2 = cv2.morphologyEx(im1, cv2.MORPH_OPEN, se2)
	return im2	

if __name__ == '__main__':
	try: path = sys.argv[1]		
	except: path = './DataSet/np5.jpg'
	try: DarkonLight = int(sys.argv[2])
	except: DarkonLight = 1
	img = cv2.imread(path,0)
	if img is None:
		print 'Failed to load image file:', path
		sys.exit(1)

	height,width= img.shape
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