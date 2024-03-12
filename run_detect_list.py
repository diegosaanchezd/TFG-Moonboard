import re
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


def nextProblem(tl_x, tl_y, br_x, br_y, SCREEN_WIDTH, SCREEN_HEIGHT):
    start_x = int(tl_x + (br_x-tl_x-200) * 0.88)
    start_y = int((tl_y+br_y+300)/2)
    end_x = start_x
    end_y = start_y - 600

    # Establece la posición inicial del cursor
    win32api.SetCursorPos((start_x, start_y))

    # Presiona el botón izquierdo del ratón
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, start_x, start_y, 0, 0)

    # Simula el movimiento del ratón hacia la posición final
    num_steps = 10  # Puedes ajustar el número de pasos según sea necesario
    for step in range(1, num_steps + 1):
        current_x = int(start_x + (end_x - start_x) * step / num_steps)
        current_y = int(start_y + (end_y - start_y) * step / num_steps)
        win32api.SetCursorPos((current_x, current_y))
        time.sleep(0.05)  # Pausa breve para simular el arrastre

    # Levanta el botón izquierdo del ratón
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, end_x, end_y, 0, 0)


def writeJSONfile(n, problem_text_list, json_decoded):
    for problem_text in problem_text_list:
        # Extract information from the problem text
        lines = problem_text.split('\n')
        problem_name_line = next((line for line in lines if any(word.isupper() for word in line.split())), None)
        
        # Extract user grade and repeats information
        user_grade_line = next((line for line in lines if "User grade" in line), None)
        repeats_line = next((line for line in lines if "repeats" in line), None)
        
        # Extract method information
        method_line = next((line for line in lines if "Any" in line), None)

        # Create the problem dictionary
        problem_dict = {
            "Name": problem_name_line,
            "UserGrade": user_grade_line,
            "Repeats": repeats_line,
            "Method": method_line
        }

        # Check if the problem with the same name already exists
        if problem_name_line is None or user_grade_line is None or repeats_line is None or method_line is None:
            pass
        else:
            index = str(len(json_decoded))
            json_decoded[index] = problem_dict



def detectText(image):
    # Cut out only the important part of the image
    x_1 = int(0.03 * (ss_region_br_x - ss_region_tl_x))
    x_2 = int(0.68 * (ss_region_br_x - ss_region_tl_x))
    y_1 = int(0.27 * (ss_region_br_y - ss_region_tl_y))
    y_2 = int(0.92 * (ss_region_br_y - ss_region_tl_y))

    img = image[y_1:y_2, x_1:x_2]

    invert = cv2.bitwise_not(img)
    text = pytesseract.image_to_string(invert)
    
    # Expresión regular para verificar si la línea sigue un formato específico
    pattern = re.compile(r'^(?:#|>>|<<| )?[A-Z0-9 !@#$%^&*()-_=+;:,.<>?/\\\'"]+$', re.MULTILINE)

    # Usar findall para encontrar todas las coincidencias
    matches = [match.start() for match in pattern.finditer(text)]

    # Iterar sobre las coincidencias y obtener los bloques entre ellas
    problems = [text[matches[i]:matches[i+1]].strip() for i in range(len(matches)-1)]
    # Agregar el último bloque después de la última coincidencia
    problems.append(text[matches[-1]:].strip() if matches else text.strip())
    
    #for i, problem in enumerate(problems):
    #    print(problem)
    #    print("-" * 40)
        
    return problems



def removeBlueColor(image):
    # Convertir la imagen de BGR a HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definir el rango de tonalidades de azul en HSV
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])

    # Crear una máscara que filtre los píxeles azules
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Invertir la máscara para obtener una máscara de los píxeles NO azules
    inverted_mask = cv2.bitwise_not(mask)

    # Aplicar la máscara a la imagen original
    result = cv2.bitwise_and(image, image, mask=inverted_mask)

    # Convertir los píxeles negros (originales azules) en blancos
    result[result == 0] = 255

    return result



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
json_path = r"C:\Users\diego\Desktop\TFG MOONBOARD\datasets\2017_problems_list_40.json"


# These values define the pixel region where the code will take a screenshot. Inside this area should
# be contained the emulator screen with the moonboard app opened on the first problem
ss_region_tl_x = 724		# screen shot region, top left, x coord
ss_region_tl_y = 19 		# screen shot region, top left, y coord
ss_region_br_x = 1192		# screen shot region, bottom right, x coord
ss_region_br_y = 977		# screen shot region, bottom left, y coord


tot_problems = 1		# Number of problems that you want to write in the dataset


# Height and width of your screen
SCREEN_WIDTH = 2340
SCREEN_HEIGHT = 1080


# ****************************************************************************************************

with open(json_path) as json_file:
    json_decoded = json.load(json_file)


# Cycle over all the problems available in the app
for n in range(0, tot_problems):
    # Capture and save screen image
    ss_region = (ss_region_tl_x, ss_region_tl_y, ss_region_br_x, ss_region_br_y)
    ss_img = ImageGrab.grab(ss_region)

    image = np.array(ss_img)

    # Remove blue color from the image
    image_without_blue = removeBlueColor(image)

    # Perform text detection on the modified image
    text = detectText(image_without_blue)

    # Write the results in a JSON file
    writeJSONfile(n, text, json_decoded)

    # Move to the next problem
    nextProblem(ss_region_tl_x, ss_region_tl_y, ss_region_br_x, ss_region_br_y, SCREEN_WIDTH, SCREEN_HEIGHT)

    print(n)


# Write everything in one json file
with open(json_path, 'w') as json_file:
    json.dump(json_decoded, json_file, sort_keys=False, indent=4, separators=(',', ': '))