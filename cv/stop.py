import numpy as np
import cv2
import imutils
from matplotlib import pyplot as plt

image = cv2.imread("C:/Users/shins/Desktop/temp/stop_sign_519.png")

# image = np.zeros(org_image.shape, org_image.dtype)
# alpha = 1 # Simple contrast control
# beta = 0    # Simple brightness control
#
# for y in range(org_image.shape[0]):
#     for x in range(org_image.shape[1]):
#         for c in range(org_image.shape[2]):
#             image[y,x,c] = np.clip(alpha*org_image[y,x,c] + beta, 0, 255)

plt.imshow(image)
plt.show()

cv2.imshow('Original Image', image)
cv2.waitKey(0)
# cv2.imshow('image', image)
# cv2.waitKey(0)

# image = cv2.cvtColor(org_image, cv2.COLOR_BGR2HSV)

boundaries = [
    ([165, 135, 220], [190, 200, 240])  #RED for STOP
]


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

    blurred = cv2.GaussianBlur(v1, (25, 25), 0)
    # thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)[1]
    # thresh = cv2.threshold(blurred, 10, 150, cv2.THRESH_BINARY)[1]

    cv2.imshow("v1", blurred)
    cv2.waitKey(0)

    # find contours in the thresholded image and initialize the
    # shape detector
    # contours, hierarchy = cv2.findContours(image, thresh.copy(), method[, contours[, hierarchy[, offset]]])
    cnts = cv2.findContours(blurred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    cv2.imshow("images", np.hstack([image, output]))
    cv2.waitKey(0)

    if idx == 0:
        if cnts != None:
            print("stop")
            M = cv2.moments(cnts[0])
            cX = int((M["m10"] / M["m00"]) * ratio)
            cY = int((M["m01"] / M["m00"]) * ratio)
            cv2.drawContours(image, [cnts[0]], -1, (0, 255, 0), 2)
            # cv2.drawContours(image, [cnts[0]], -1, (0, 255, 0), 2)
            epsilon = cv2.arcLength(cnts[0], True)
            approx = cv2.approxPolyDP(cnts[0], epsilon, True)
            print(epsilon)
            print(approx)
            cv2.putText(image, "stop", (cX - 20, cY - 70), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (200, 100, 255), 2)

        continue

    # for c in cnts:
    #     # compute the center of the contour, then detect the name of the
    #     # shape using only the contour
    #
    #
    #     M = cv2.moments(c)
    #     cX = int((M["m10"] / M["m00"]) * ratio)
    #     cY = int((M["m01"] / M["m00"]) * ratio)
    #     # shape = detect(c)
    #     shape = "NONE"
    #
    #     # multiply the contour (x, y)-coordinates by the resize ratio,
    #     # then draw the contours and the name of the shape on the image
    #     c = c.astype("float")
    #     c *= ratio
    #     c = c.astype("int")
    #     cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
    #     cv2.putText(image, shape, (cX-20, cY-70), cv2.FONT_HERSHEY_SIMPLEX,
    #                 0.5, (150, 100, 255), 2)


cv2.imshow("images", np.hstack([image, output]))
cv2.waitKey(0)