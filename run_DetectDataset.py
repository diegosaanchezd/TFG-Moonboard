import cv2 
import numpy as np
import matplotlib.pyplot as plt 
from PIL import ImageGrab
import time
import win32api, win32con
import json
import pytesseract




# -------------------------------------------------------
#    _____ _   _ _   _  ____ _____ ___ ___  _   _ ____  
#   |  ___| | | | \ | |/ ___|_   _|_ _/ _ \| \ | / ___| 
#   | |_  | | | |  \| | |     | |  | | | | |  \| \___ \ 
#   |  _| | |_| | |\  | |___  | |  | | |_| | |\  |___) |
#   |_|    \___/|_| \_|\____| |_| |___\___/|_| \_|____/ 
#
# -------------------------------------------------------




def detectCircle(image, name, verbose):

	all_circs = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1.2, 30, param1=60, param2=40, minRadius=0, maxRadius=1000)
	
	if(all_circs is None):
		all_circs_rounded = []
	else:
		all_circs_rounded = np.uint16(np.around(all_circs))

	count = 1
	if(all_circs is not None):
		for i in all_circs_rounded[0,:]:
			cv2.circle(image, (i[0],i[1]),i[2],(50,200,200),5)
			cv2.circle(image, (i[0],i[1]),2,(255,0,0),3)
			count +=1

	if(verbose==1):
		cv2.imshow(name, image)
		cv2.waitKey(0)

	return all_circs_rounded




def closestHold(y,x,holds_pos):
	lett_str = ["A","B","C","D","E","F","G","H","I","J","K"]
	num_str = ["12","11","10","9","8","7","6","5","4","3","2","1"]

	# find the closest on y axis
	ymin = 1000
	for i in range(0,12):
		ydist = np.abs(y-holds_pos[i,0,0])
		if(ydist < ymin):
			ymin = ydist
			closest_row = i
	# find the closest on x axis
	xmin = 1000
	for j in range(0,11):
		xdist = np.abs(x-holds_pos[0,j,1])
		if(xdist < xmin):
			xmin = xdist
			closest_col = j
	
	return [num_str[closest_row], lett_str[closest_col]]



def nextProblem(tl_x, tl_y, br_x, br_y, SCREEN_WIDTH, SCREEN_HEIGHT):
    
	x = int(tl_x + (br_x-tl_x) * 0.88)
	y = int((tl_y+br_y)/2)

	# move to roght side of the app
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/SCREEN_WIDTH*65535.0), int(y/SCREEN_HEIGHT*65535.0))  
	# press the left button 
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)

	# slightly drag the clicked mouse to the left
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int((x-50)/SCREEN_WIDTH*65535.0), int(y/SCREEN_HEIGHT*65535.0)) 
	# let go the left button     
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x-50,y,0,0)



def writeJSONfile(n, r_hold, g_hold, b_hold, text, json_decoded):

	# Write the json informations
	problem_name = text[0]
	problem_grade = text[1]
 
	if (problem_name == '' or problem_grade == '' or problem_grade.startswith('‘Any marked holds')):
		return

	if problem_grade.startswith('TAH'):
		problem_grade = '7A+'
  
	elif problem_grade.startswith('TAA'):
		problem_grade = '7A+'
  
	elif problem_grade.startswith('TAN'):
		problem_grade = '7A+'
  
	elif problem_grade.startswith('TA'):
		problem_grade = '7A'
  
	elif problem_grade.startswith('TC'):
		problem_grade = '7C'
  
	elif problem_grade.startswith('TC+'):
		problem_grade = '7C+'
  
	elif problem_grade.startswith('TB'):
		problem_grade = '7B'
  
	elif problem_grade.startswith('TB+'):
		problem_grade = '7B+'
  
	elif problem_grade.startswith('BA'):
		problem_grade = '8A'
  
	elif problem_grade.startswith('BB'):
		problem_grade = '8B'
  
	elif problem_grade.startswith('BC'):
		problem_grade = '8C'
  
	elif problem_grade.startswith('OA'):
		problem_grade = '6A'
  
	elif problem_grade.startswith('OB'):
		problem_grade = '6B'
	
	elif problem_grade.startswith('OC'):
		problem_grade = '6C'

	
	problem_dict = {
        "Name" : problem_name,
        "Grade" : problem_grade,
        "Moves" : [],
    	"Sended": False
    }

	# Cycle over red holds - TOP
	for k in range(0, len(r_hold)):

		hold_name = str(r_hold[k][0])+str(r_hold[k][1])
		hold_start = False
		hold_top = True

		move_dict = {
					"Description": hold_name,
					"IsStart": hold_start,
					"IsEnd": hold_top
		}

		problem_dict["Moves"].append(move_dict)

	# Cycle over blue holds - MIDDLE
	for k in range(0, len(b_hold)):

		hold_name = str(b_hold[k][0])+str(b_hold[k][1])
		hold_start = False
		hold_top = False

		move_dict = {
					"Description": hold_name,
					"IsStart": hold_start,
					"IsEnd": hold_top
		}

		problem_dict["Moves"].append(move_dict)

	# Cycle over green holds - START
	for k in range(0, len(g_hold)):

		hold_name = str(g_hold[k][0])+str(g_hold[k][1])
		hold_start = True
		hold_top = False

		move_dict = {
					"Description": hold_name,
					"IsStart": hold_start,
					"IsEnd": hold_top
		}

		problem_dict["Moves"].append(move_dict)

	if any(item['Name'] == problem_name for item in json_decoded.values()):
		pass
	else:
		json_decoded[str(n)] = problem_dict
     	




def detectText(image):
    
	# cut out only the important part of the image
	x_1 = int(0.17*(ss_region_br_x-ss_region_tl_x))
	x_2 = int(0.88*(ss_region_br_x-ss_region_tl_x))
	y_1 = int(0.10*(ss_region_br_y-ss_region_tl_y))
	y_2 = int(0.20*(ss_region_br_y-ss_region_tl_y))

	img = image[y_1:y_2, x_1:x_2]
 
	invert = cv2.bitwise_not(img) 
	text = pytesseract.image_to_string(invert)
	line = text.split('\n')
	line[1] = line[2].split('/')[0]
	if(len(line) < 2):
		line.append('NA')

	return line




# --------------------------------
#    __  __    _    ___ _   _ 
#   |  \/  |  / \  |_ _| \ | |
#   | |\/| | / _ \  | ||  \| |
#   | |  | |/ ___ \ | || |\  |
#   |_|  |_/_/   \_\___|_| \_|
#
# --------------------------------




# THINGS TO MODIFY FOR MAKING IT WORK ON ANY COMPUTER
# ****************************************************************************************************


# Open JSON file
json_path = r"C:\Users\diego\Desktop\TFG MOONBOARD\2020_problems_40.json"


# These values define the pixel region where the code will take a screenshot. Inside this area should
# be contained the emulator screen with the moonboard app opened on the first problem
ss_region_tl_x = 724		# screen shot region, top left, x coord
ss_region_tl_y = 19 		# screen shot region, top left, y coord
ss_region_br_x = 1192		# screen shot region, bottom right, x coord
ss_region_br_y = 977		# screen shot region, bottom left, y coord


tot_problems = 5600		# Number of problems that you want to write in the dataset


# Height and width of your screen
SCREEN_WIDTH = 2340
SCREEN_HEIGHT = 1080


# These are the values that will define where are the real holds, need to fine tune this depending on your screen
yoff = 375
xoff = 65
x_sep = 38
y_sep = 38

# ****************************************************************************************************




with open(json_path) as json_file:
    json_decoded = json.load(json_file)


# Cycle over all the problems available in the app
for n in range(0, tot_problems):

	# Capture and save screen image 
	ss_region = (ss_region_tl_x,ss_region_tl_y, ss_region_br_x, ss_region_br_y)
	ss_img = ImageGrab.grab(ss_region)

	image = np.array(ss_img)
 
	img = image[:, :, ::-1]

	text = detectText(image)

	# Exctract the circles (B,G,R)
	low_r  = np.array([0, 0, 220])				# minimum color red accepted in the mask
	high_r = np.array([65, 53, 255])			# maximum color red accepted in the mask
	maskR  = cv2.inRange(img, low_r, high_r)

	low_b  = np.array([230, 0, 0])
	high_b = np.array([255, 96, 55])
	maskB  = cv2.inRange(img, low_b, high_b)

	low_g  = np.array([0, 225, 0])
	high_g = np.array([90, 255, 25])
	maskG  = cv2.inRange(img, low_g, high_g)
 
	# Detect the centers and radiuses of circles
	red_circles   = detectCircle(maskR, "red detection",0)
	blue_circles  = detectCircle(maskB, "blue detection",0)
	green_circles = detectCircle(maskG, "green detection",0)

	# Create matrix that contains the real holds positions, need to fine tune parameter depending on the screen
	holds_pos = np.zeros((12,11,2))
	for j in range(0,12):
		for i in range(0,11):
			holds_pos[j,i,1] = xoff+x_sep*i
			holds_pos[j,i,0] = yoff+y_sep*j

			# ******** Uncomment the line below to debug and fine tune the parameters ********
			#cv2.circle(img, (xoff+x_sep*i,yoff+y_sep*j),2,(255,0,0),3)

	# ******** Uncomment the line below to debug and fine tune the parameters ********
	#cv2.imshow('moon', img)
	#cv2.waitKey(0)


	# Assign to each fiund circle the closes real hold
	r_hold = []
	b_hold = []
	g_hold = []

	if type(red_circles) is not list:
		for i in range(0,red_circles.shape[1]):
			hold = closestHold(red_circles[0,i,1],red_circles[0,i,0], holds_pos)
			r_hold.append(hold)

	if type(blue_circles) is not list:
		for i in range(0,blue_circles.shape[1]):
			hold = closestHold(blue_circles[0,i,1],blue_circles[0,i,0], holds_pos)
			b_hold.append(hold)

	if type(green_circles) is not list:
		for i in range(0,green_circles.shape[1]):
			hold = closestHold(green_circles[0,i,1],green_circles[0,i,0], holds_pos)
			g_hold.append(hold)


	# Write the results in a JSON file
	writeJSONfile(n, r_hold, g_hold, b_hold, text, json_decoded)


	nextProblem(ss_region_tl_x, ss_region_tl_y, ss_region_br_x, ss_region_br_y, SCREEN_WIDTH, SCREEN_HEIGHT)
	print(n)


# Write everything in one json file
with open(json_path, 'w') as json_file:
    json.dump(json_decoded, json_file, sort_keys=False, indent=4, separators=(',', ': '))