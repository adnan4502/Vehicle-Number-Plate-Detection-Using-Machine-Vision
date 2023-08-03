import re
import cv2
import imutils
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"c:\Program Files\Tesseract-OCR\tesseract.exe"

# Read image
image = cv2.imread('9100.jpg')

# Resize image
image = imutils.resize(image, width=500)

# Show original image
cv2.imshow("Original image", image)
cv2.waitKey(0)

# Gray scale image to reduce dimension and complexity of image
# e.g. Canny only works on gray image
gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

# Reduce noise from image
gray = cv2.bilateralFilter(gray, 11, 17, 17)

# Find the edges of image
edged = cv2.Canny(gray, 170, 200)

# Find the contours based on the image
cnts, new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# cnts is contours which means that it is like the curve joining all the contour points
# new is hierarchy - relationship
# RETR_LIST retrieves all the contours but does not create any parent-child relationship
# CHAIN_APPROX_SIMPLE removes all the redundant points and compress the contour by saving memory

# Create a copy of image to draw all the contours which are identified on continuous structure
image1 = image.copy()
cv2.drawContours(image1, cnts, -1, (0, 255, 0), 3)  # the values are fixed'

# To select the interested contours of number plate, we will sort them on the basis of areas
# Top 30 areas will be sorted and listed in the order of max to min
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
NumberPlateCount = None

# Create a copy of image to draw top 30 contours so that won't affect the original image
image2 = image.copy()
cv2.drawContours(image2, cnts, -1, (0, 255, 0), 3)

count = 0
name = 1    # name of our image (cropped image)

for i in cnts:
    perimeter = cv2.arcLength(i, True)
    # arcLength = perimeter
    approx = cv2.approxPolyDP(i, 0.05*perimeter, True)
    # approxPolyDP can approximate the curve of polygon with precision
    if len(approx) == 4:    # 4 means it has 4 corners, possibly it is number plate
        NumberPlateCount = approx
        # crop the rectangle part
        x, y, w, h = cv2.boundingRect(i)
        crp_img = image[y:y+h, x:x+w]
        cv2.imwrite(str(name)+'.jpg', crp_img)
        name += 1

        break

# Show Final Image (number plate with rectangle boundary)
cv2.drawContours(image, [NumberPlateCount], -1, (0, 255, 0), 3)
cv2.imshow("Final Image", image)
cv2.waitKey(0)

# Show Cropped Image (only the number plate)
crop_img_loc = '1.jpg'
cv2.imshow("Cropped Image", cv2.imread(crop_img_loc))
cv2.waitKey(0)

# Show the text of plate number
text = pytesseract.image_to_string(crop_img_loc, lang='eng')
text = re.sub(r'[^a-zA-Z0-9]+', '', text)      # Remove all symbols from the text and only show alphabet and letters
print("Number: ", text)
cv2.waitKey(0)


# Function to match the number plate obtained with predefined number plates
def match_plate(string_list, target_value):
    for string in string_list:
        if string == target_value:
            print("Number plate matches. Opening gate.")
            return
    print("Error! Cannot enter!")


# Predefined number plate values
number_plates = ["SMS1", "MAH41", "GHI1234"]
match_plate(number_plates, text)