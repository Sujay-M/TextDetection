import cv2
import numpy as np
from random import randint
def draw_mask(event,x,y,flags,param):
	global ix,iy,drawing
	if event == cv2.EVENT_LBUTTONDOWN:
		ix,iy = x,y
	elif event == cv2.EVENT_LBUTTONUP:			
		drawing = True

def masker():
	cv2.namedWindow('image')
	global ix,iy,drawing,CC,count,Mask
	cv2.setMouseCallback('image',draw_mask)
	while(1):
		if drawing==True:
			i=CC.item(iy,ix)
			if i!=0:
				Index = np.where(CC==i)
				count = count+1
				pts.append(i)
				masks.append(Mask.copy())
				Mask[Index]  = 255
				drawing = False			
		show = orig.copy()
		show[Mask>0] = [0,0,0]
		cv2.imshow('image',show)
		k = cv2.waitKey(1) & 0xFF		
		if k == ord('u') or k == ord('U'):
			if count>0:
				del masks[count]
				del pts[count-1]
				count = count-1
				Mask = masks[count].copy()
			else:
				Mask[:,:] = 0
		elif k == 27:
			break
	cv2.destroyAllWindows()
def createMask(img):
	global orig,Mask,masks,CC
	orig = img.copy()
	orig = cv2.cvtColor(orig,cv2.COLOR_GRAY2RGB)
	h,w,_ = orig.shape	
	no,CC,stats,Cen = cv2.connectedComponentsWithStats(img)
	for i in range(1,no):
		c=[randint(2,255),randint(2,255),randint(2,255)]
		Index = np.where(CC==i)
		orig[Index] = c	
	Mask = np.zeros((h,w),np.uint8)
	masks.append(Mask.copy())	
	masker()
	masks = []
	drawing = False
	return Mask,pts
CC = np.empty(0)
Mask = np.empty(0)
orig = np.empty(0)
masks = []
pts = []
ix = -1
iy = -1
drawing = False
count = 0