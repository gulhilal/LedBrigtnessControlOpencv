import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import serial

arduino = serial.Serial('COM4', 9600)  # com4'ü açar 9600 baudrate ile bağlanır

########################
wCam, hCam = 640, 480    # kamera penceresinin genişliği ve uzunluğu belirlenir
########################

cap = cv2.VideoCapture(0)  # webcam'in açılması
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0  # FPS hesaplanırken kullnaıldı

detector = htm.handDetector(detectionCon=0.7)  # HandTrackingModule kütüphanesindeki handDetector sınıfından bir obje oluşturuldu

brightnessBar = 150  # parlaklık seviyesini gösteren bar başlangıçta en düşük seviyede tanımlandı
brightnessPer = 0      # parlaklık seviyesi başlangıçta en düşük seviyede tanımlandı

while True:
    success, img = cap.read()
    img = detector.findHands(img)  # findHands metodu ile kamerada el tespit edildi ve img'a atandı
    PosList = detector.findPosition(img, draw=False)   # PosList'e findPosition'dan gelen liste atandı.
    if len(PosList) != 0:                              # Bu listede elin 20 noktasının pozisyonları bulunuyor
        x1, y1 = PosList[4][1], PosList[4][2]   # 4 baş parmağı 8 de işaret parmağını temsil ediyor bu yüzden bu noktaların x ve y
        x2, y2 = PosList[8][1], PosList[8][2]   # değerleri değişkenlere atanıyor
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # iki noktanın ortası bulunuyor

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)  # Baş parmak işaret parmağı ve merkeze daire çiziliyor
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)  # Baş parmak ile işaret parmağı arasına çizgi çiziliyor


        length = int(math.hypot(x2 - x1, y2 - y1))  # baş parmak ile işaret parmağı arasındaki uzunluk bulunuyor
        # print (length)
        # print(length.bit_length())

        if length < 30:  # parmaklar tam kapanınca merkezdeki dairenin rengi yeşil oluyor
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)


        length = int(np.interp(length, [30, 280], [0, 255]))  # 30-280 arasında değişen uzunluk değerleri 0-255'e dönüştürülüyor.
                                                              # Bu değerler seri porta gönderileceği için 0-255 arasında olmalı.

        brightnessBar = np.interp(length, [0, 255], [400, 150]) # parlaklık seviyesinde 0->400'e 255->150 ye dönüştürülüyor.
        brightnessPer = np.interp(length, [0, 255], [0, 100])  # yüzde parlaklık seviyesinde 0->0'a 255->100'e dönüştürülüyor

        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 255), 3)  # (50, 150), (85, 400) konumunda bir dikdörtgen oluşturuluyor
        cv2.rectangle(img, (50, int(brightnessBar)), (85, 400), (255, 0, 255), cv2.FILLED) # oluşturulan dikdörtgenin içi parlaklık seviyesine göre dolduruluyor.
        cv2.putText(img, f'{int(brightnessPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2) # parlaklık yüzdesi oluşturulan dikdörtgen barın altına yazılıyor.


        arduino.write(bytes([length])) # iki parmak arasındaki uzunluk değeri arduinoya gönderiliyor

        print(f'Seri Porta Gönderilen Deger: ', length) # seri porta gönderilen değer ekrana yazdırılıyor


        if length == 0:  # seri porta gönderilen değer 0 ise LED SONDU yazısı palaklık yüzddesinin yanında yazıyor
            cv2.putText(img, f'(LED SONDU.)', (100, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

        if length == 255:  # seri porta gönderilen değer 255 ise MAXIMUM PARLAKLIK yazısı palaklık yüzddesinin yanında yazıyor
            cv2.putText(img, f'(MAXIMUM PARLAKLIK.)', (140, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)


    cTime = time.time()  # saniye cinsinden şimdiki zamanı veriyor
    fps = 1 / (cTime - pTime) # FPS hesaplanıyor
    pTime = cTime

    cv2.putText(img, f'FPS:{int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3) # FPS değeri ekranın sol üst köşesine yazdırılıyor.

    cv2.imshow("Img", img)
    cv2.waitKey(1)
