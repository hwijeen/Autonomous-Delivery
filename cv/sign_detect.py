import numpy as np
import cv2
import imutils
from matplotlib import pyplot as plt

org_image = cv2.imread("C:/Users/shins/Desktop/temp/stop_sign_162.png")
# cv2.imshow("org", org_image)
# cv2.waitKey(0)

image = np.zeros(org_image.shape, org_image.dtype)
alpha = 1.3 # Simple contrast control
beta = 28    # Simple brightness control


for y in range(org_image.shape[0]):
    for x in range(org_image.shape[1]):
        for c in range(org_image.shape[2]):
            image[y,x,c] = np.clip(alpha*org_image[y,x,c] + beta, 0, 255)


cv2.imshow('Original Image', org_image)
cv2.waitKey(0)
cv2.imshow('image Image', image)
# cv2.imshow("new", new_image)
cv2.waitKey(0)

plt.imshow(image)
plt.show()

# org_image = cv2.resize(org_image, (500, 700))
image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

DIGITS_LOOKUP = {
    (1, 1, 1, 0, 1, 1, 1): 0,
    (0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 1, 1, 1, 0): 2,
    (1, 0, 1, 1, 0, 1, 1): 3,
    (0, 1, 1, 1, 0, 1, 0): 4,
    (1, 1, 0, 1, 0, 1, 1): 5,
    (1, 1, 0, 1, 1, 1, 1): 6,
    (1, 0, 1, 0, 0, 1, 0): 7,
    (1, 1, 1, 1, 1, 1, 1): 8,
    (1, 1, 1, 1, 0, 1, 1): 9
}

def detect(c):
    # initialize the shape name and approximate the contour
    shape = "unidentified"
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.04 * peri, True)

    # if the shape is a triangle, it will have 3 vertices
    if len(approx) == 3:
        shape = "triangle"

    # if the shape has 4 vertices, it is either a square or
    # a rectangle
    elif len(approx) == 4:
        # compute the bounding box of the contour and use the
        # bounding box to compute the aspect ratio
        (x, y, w, h) = cv2.boundingRect(approx)
        # import pdb
        # pdb.set_trace()
        print(w, h)

        ar = w / float(h)

        # a square will have an aspect ratio that is approximately
        # equal to one, otherwise, the shape is a rectangle
        shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"

    # otherwise, we assume the shape is a circle
    else:
        shape = "octagon"
    return shape

# define the list of boundaries
boundaries = [  #BGR
	# ([17, 15, 100], [50, 56, 200]),  #RED RGB
    # ([0, 50, 50], [10, 255, 255]),  #RED
    # ([161, 155, 84], [179, 255, 255]),
    # ([36, 25, 25], [70, 255,255])  #GREEN
    ([30, 150, 100], [70, 250, 200])  #GREEN
]

# loop over the boundaries
for idx, (lower, upper) in enumerate(boundaries):

    # create NumPy arrays from the boundaries
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    # find the colors within the specified boundaries and apply
    # the mask
    mask = cv2.inRange(image, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)

    ratio = image.shape[0] / float(output.shape[0])

    # convert the resized image to grayscale, blur it slightly,
    # and threshold it
    # gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    h, s, v1 = cv2.split(output)

    blurred = cv2.GaussianBlur(v1, (21, 21), 0)
    thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)[1]

    cv2.imshow("v1", thresh)
    cv2.waitKey(0)

    # find contours in the thresholded image and initialize the
    # shape detector
    # contours, hierarchy = cv2.findContours(image, thresh.copy(), method[, contours[, hierarchy[, offset]]])
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    cv2.imshow("images", np.hstack([org_image, output]))
    cv2.waitKey(0)

    if idx == 0:
        if cnts != None:
            cv2.imshow("stop", cnts[0])
            cv2.waitKey(0)
            print("stop")
            M = cv2.moments(cnts[0])
            cX = int((M["m10"] / M["m00"]) * ratio)
            cY = int((M["m01"] / M["m00"]) * ratio)
            cv2.drawContours(org_image, [cnts[0]], -1, (0, 255, 0), 2)
            cv2.putText(org_image, "stop", (cX - 20, cY - 70), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (200, 100, 255), 2)

        continue

    for c in cnts:
        # compute the center of the contour, then detect the name of the
        # shape using only the contour


        M = cv2.moments(c)
        cX = int((M["m10"] / M["m00"]) * ratio)
        cY = int((M["m01"] / M["m00"]) * ratio)
        shape = detect(c)

        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        c *= ratio
        c = c.astype("int")
        cv2.drawContours(org_image, [c], -1, (0, 255, 0), 2)
        cv2.putText(org_image, shape, (cX-20, cY-70), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (150, 100, 255), 2)


cv2.imshow("images", np.hstack([org_image, output]))
cv2.waitKey(0)
