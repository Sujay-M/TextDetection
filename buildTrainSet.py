import cv2
import numpy as np
import sys
import swt
import freeHand
import connUnMask
def MserAnalysis(mser,img):
	'Analyzes mser region properties to segment connected regions'
	no,CC,stats,Cen = cv2.connectedComponentsWithStats(mser)
	newMask = np.zeros(mser.shape,np.uint8)
	imMask = np.zeros(mser.shape,np.uint8)
	for i in range(1,no):
		imMask[:,:] = 0
		Index = np.where(CC==i)		
		mean = np.mean(img[Index])
		imMask[Index]  = 255
		roi = img[stats.item(i,1):stats.item(i,1)+stats.item(i,3),stats.item(i,0):stats.item(i,0)+stats.item(i,2)]
		ret2,th = cv2.threshold(roi,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		if mean>ret2:
			imMask[stats.item(i,1):stats.item(i,1)+stats.item(i,3),stats.item(i,0):stats.item(i,0)+stats.item(i,2)]=cv2.bitwise_and(th,imMask[stats.item(i,1):stats.item(i,1)+stats.item(i,3),stats.item(i,0):stats.item(i,0)+stats.item(i,2)])
		else:
			imMask[stats.item(i,1):stats.item(i,1)+stats.item(i,3),stats.item(i,0):stats.item(i,0)+stats.item(i,2)]=cv2.bitwise_and(cv2.bitwise_not(th),imMask[stats.item(i,1):stats.item(i,1)+stats.item(i,3),stats.item(i,0):stats.item(i,0)+stats.item(i,2)])
		newMask = cv2.bitwise_or(newMask,imMask)
	return newMask
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
def createTrainSet(img):
	mser = cv2.MSER_create()
	regions = mser.detectRegions(img, None)
	mask = np.zeros(img.shape, np.uint8)
	for points in regions:
		for point in points:
			mask.itemset(point[1],point[0],255)	
	newMask = MserAnalysis(mask,img)
	textRegion = cv2.resize(freeHand.createMask(cv2.resize(img,(winWidth,winHeight))),(width,height))
	textRegion = cv2.bitwise_and(textRegion,newMask)
	no,CC,stats,Cen = cv2.connectedComponentsWithStats(textRegion)
	[text,pts] = connUnMask.createMask(cv2.resize(textRegion,(winWidth,winHeight)))
	newText = textRegion.copy()
	for i in pts:
		Index = np.where(CC==i)
		newText[Index]  = 0
	display(newText)
	return newText

MAX_AREA = 10000
MIN_AREA = 50
MAX_ASPECT_RATIO = 2
MIN_SOLIDITY = .4
MIN_ECCENTRICITY = .995
MAX_WIDTH = 1280
MAX_HEIGHT = 720
if __name__ == '__main__':
	try: path = sys.argv[1]		
	except: path = './DataSet/poster.jpg'
	try: num = int(sys.argv[2])
	except: num = 100
	img = cv2.imread(path,0)
	if img is None:
		print 'Failed to load image file:', path
		sys.exit(1)

	height,width = img.shape
	winHeight = height
	winWidth = width
	ratio = float(winHeight)/winWidth
	if winHeight>MAX_HEIGHT:
		winHeight = MAX_HEIGHT
		winWidth = int(winHeight/ratio)
	if winWidth>MAX_WIDTH:
		winWidth = MAX_WIDTH
		winHeight = int(winWidth*ratio)
	Final = createTrainSet(img)
	ch = raw_input('do u want to save the mask')
	if ch=='y' or ch=='Y':
		cv2.imwrite('./out/'+str(num)+'.png',Final)