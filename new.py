import cv2
import numpy as np
import sys

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


def applyMask(img,mask):
	no,CC,stats,Cen = cv2.connectedComponentsWithStats(mask)
	newMask = np.zeros(mask.shape,np.uint8)
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

def getMask(img):
	mser = cv2.MSER_create()
	regions = mser.detectRegions(img, None)
	mask = np.zeros(img.shape, np.uint8)
	for points in regions:
		for point in points:
			mask.itemset(point[1],point[0],255)
	return mask

def textRegions(img):
	mask = getMask(img)
	refinedMask = applyOtsu(img,mask)

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