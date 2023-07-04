import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import serial

arduino = serial.Serial('COM4', 9600)  # opens com4 connects with baudrate of 9600

########################
wCam, hCam = 640, 480    # the width and length of the camera window are determined
########################

cap = cv2.VideoCapture(0)  # opening webcam
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0  # used when calculating FPS

detector = htm.handDetector(detectionCon=0.7)  # Created an object from the handDetector class in the HandTrackingModule library

brightnessBar = 150  # bar showing the brightness level was initially defined at the lowest level
brightnessPer = 0      # the brightness level was initially defined at the lowest level
while True:
    success, img = cap.read()
    img = detector.findHands(img)  # Hand detected on camera with findHands method and assigned to img
    PosList = detector.findPosition(img, draw=False)   # List from findPosition is assigned to PosList.
    if len(PosList) != 0:                              # This list contains the positions of the 20 points of the hand.
        x1, y1 = PosList[4][1], PosList[4][2]   # 4 thumbs represent 8 index fingers so x and y values of these points are assigned to variables
        x2, y2 = PosList[8][1], PosList[8][2]   
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # find the middle of two points and assign cx and cy

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)  # Thumb, forefinger and center circled
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)  # Drawing a line between thumb and forefinger


        length = int(math.hypot(x2 - x1, y2 - y1))  # the length between thumb and index finger is found and assigned to length
        # print (length)
        # print(length.bit_length())

        if length < 30:  # When the fingers are fully closed, the color of the circle in the center turns green.
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)


        length = int(np.interp(length, [30, 280], [0, 255]))  # Length values ranging from 30-280 are converted to 0-255.
                                                              # Since these values will be sent to the serial port, they should be between 0-255.

        brightnessBar = np.interp(length, [0, 255], [400, 150]) # It is converted to 0->400 at brightness level to 255->150.
        brightnessPer = np.interp(length, [0, 255], [0, 100])  # converting from 0->0 to 255->100 at percent brightness level

        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 255), 3)  # Creating a rectangle at (50, 150), (85, 400)
        cv2.rectangle(img, (50, int(brightnessBar)), (85, 400), (255, 0, 255), cv2.FILLED) # The inside of the created rectangle is filled according to the brightness level.
        cv2.putText(img, f'{int(brightnessPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2) # The brightness percentage is written under the created rectangular bar.


        arduino.write(bytes([length])) # length value between two fingers is sent to arduino

        print(f'Value Sent to Serial Port: ', length) # the value sent to the serial port is printed 


        if length == 0:  # If the value sent to the serial port is 0, LED OFF is written next to the brightness percentage.
            cv2.putText(img, f'(LED OFF.)', (100, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

        if length == 255:  # If the value sent to the serial port is 255, MAXIMUM BRIGHTNESS is written next to the brightness percentage.
            cv2.putText(img, f'(MAXIMUM BRIGHTNESS.)', (140, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)


    cTime = time.time()  # Returns the current time in seconds
    fps = 1 / (cTime - pTime) # Calculating FPS
    pTime = cTime

    cv2.putText(img, f'FPS:{int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3) # FPS value is printed in the upper left corner of the screen.

    cv2.imshow("Img", img)
    cv2.waitKey(1)
