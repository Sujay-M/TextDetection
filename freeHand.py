import cv2
import numpy as np
'''
FreeHand Convex PolyGon Mask creation tool

Usage: use mouse select the polygon points
Keys:
  c|C     - Create a mask from the current set of polygon points
  n|N 	  - A new convex polygon mask along side the current one. 
  			(after creation of one mask if this is not done 
  				new set of points will be considered as part of the old one )
			(new also acts as commit for using undo)
  u|U 	  - Undo
  e|E 	  - Eraser tool (size 10) 
  ESC   - exit
'''
def draw_mask(event,x,y,flags,param):
	global ix,iy,drawing,pts,draw,mask,erase,size
	if erase==-1:
		if event == cv2.EVENT_LBUTTONDOWN:
			drawing = True
			ix,iy = x,y
			pts.append((x,y))
		elif event == cv2.EVENT_MOUSEMOVE:
			if drawing == True:
				cv2.line(draw,(ix,iy),(x,y),255,1)
				pts.append((x,y))
				ix,iy = x,y       	
		elif event == cv2.EVENT_LBUTTONUP:
			mask = draw | mask
			draw[:,:] = 0
			pts.append((x,y))
			drawing = False
	else:
		if event == cv2.EVENT_LBUTTONDOWN:
			drawing = True
			cv2.circle(draw, (x,y), size,255,1)
			cv2.circle(mask, (x,y), size,0,-1)
		elif event == cv2.EVENT_MOUSEMOVE:
			if drawing == True:
				draw[:,:] = 0
				cv2.circle(draw, (x,y), size,255,1)
				cv2.circle(mask, (x,y), size,0,-1)
			else:
				draw[:,:] = 0
				cv2.circle(draw, (x,y), size,255,1)
		elif event == cv2.EVENT_LBUTTONUP:
			drawing = False       	
def masker():
	cv2.namedWindow('image')
	global draw,pts,mask,count,erase,size
	cv2.setMouseCallback('image',draw_mask)
	while(1):
		show = orig.copy()
		if erase==-1:
			show[draw>0] = [255,0,0]
		else:
			show[draw>0] = [255,255,255]
		show[mask>0] = [0,0,255]
		cv2.imshow('image',show)
		k = cv2.waitKey(1) & 0xFF
		if k == ord('u') or k == ord('U'):
			if count>0:
				del masks[count]
				count = count-1
				mask = masks[count].copy()
			else:
				mask[:,:] = 0
			del pts[:]
		elif (k==ord('c') or k==ord('C')) and len(pts)>1:
			points = np.array(pts)
			cv2.fillConvexPoly(mask,points,255)
		elif k==ord('n') or k==ord('N'):
			count=count+1
			masks.append(mask.copy())
			del pts[:]
		elif k==ord('e') or k==ord('E'):
			erase = erase*-1
			draw[:,:] = 0
		elif k == 27:
			break
	cv2.destroyAllWindows()
def createMask(img):
	global h,w,draw,orig,mask,masks
	
	orig = img.copy()
	orig = cv2.cvtColor(orig,cv2.COLOR_GRAY2RGB)
	h,w,_ = orig.shape	
	draw = np.zeros((h,w),np.uint8)
	mask = np.zeros((h,w),np.uint8)	
	masks.append(mask.copy())	
	masker()
	return mask
h,w=0,0
pts = list()
ix,iy = -1,-1
draw = np.empty(0)
mask = np.empty(0)
orig = np.empty(0)
erase = -1
size = 3
drawing = False
count = 0
masks = []
if __name__=='__main__':
	import sys
	try: path = sys.argv[1]
	except: path = './DataSet/text.png'
	print __doc__
	orig = cv2.imread(path)
	h,w,_ = orig.shape	
	draw = np.zeros((h,w),np.uint8)
	mask = np.zeros((h,w),np.uint8)	
	masks.append(mask.copy())	
	masker()
	cv2.imshow('mask',mask)
	cv2.waitKey(0)
	cv2.destroyAllWindows()