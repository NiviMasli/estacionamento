import cv2
import pickle
import cvzone
import numpy as np
import threading
import queue

q = queue.Queue()

ARQ_POS = "PosEstacionamento"
alt, compr = 45 , 25#70, 40

with open(ARQ_POS, 'rb') as arq:
    posList = pickle.load(arq)

def checkVaga(imgProcessada, frame):
    vagas = 0

    for i,pos in enumerate(posList):
        if len(posList)>1:
            pos_ant=posList[i-1]
        if i%2!=0:

            imgCrop = imgProcessada[pos_ant[1]:pos[1], pos_ant[0]:pos[0]]
            # cv2.imshow(str(x*y),imgCrop)
            countPixels = cv2.countNonZero(imgCrop)
            cvzone.putTextRect(frame, str(countPixels), (pos_ant[0], pos_ant[1] - 3), scale=1, thickness=1, offset=0, colorR=(0, 0, 0))

            if countPixels < 300:
                cor = (0, 255, 0)
                thickness = 3
                vagas += 1
            else:
                cor = (0, 0, 255)
                thickness = 2
            cv2.rectangle(frame, pos_ant, pos, cor, thickness)
            cvzone.putTextRect(frame, f'Vagas: {vagas}/{int((len(posList)/2)//1)}', (20, 55), scale=4, thickness=5, offset=20,
                               colorR=(0, 0, 0))


def Processamento(frame):

    imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)  # TESTAR PARAM
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)  # TESTAR PARAM 2
    imgMedian = cv2.medianBlur(imgThreshold, 5)  # TESTAR PARAM 3
    kernel = np.ones((3, 3), np.uint8)  # TESTAR PARAM 4
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)  # TESTAR PARAM 5
    return imgDilate


def Receive():
    # r'rtsp://admin:SSYRMI@192.168.0.244:554/Streaming/Channels/401'

    rtsp_url=r'rtsp://admin:SSYRMI@192.162.254.100:554/cam/realmonitor?channel=1&subtype=0'
    #rtsp_url =r'rtsp://admin:SSYRMI@192.168.0.244:554/video'
    #rtsp_url = r'rtsp://admin:SSYRMI@192.168.0.244:554'
    #rtsp_url = r'rtsp://admin:SSYRMI@192.168.0.244' Port emitido -> valor padrão (554)
    #rtsp_url='sample.mp4'
    camera = cv2.VideoCapture(rtsp_url)

    while True:
        if threads[1].is_alive():
            validacao, frame = camera.read()
            if not validacao:
                print('validacao false')
                camera.release()
                camera=cv2.VideoCapture(rtsp_url)
                _, frame = camera.read()

            #frame=cv2.flip(frame,0)
            frame = cv2.resize(frame, (854, 480))  # RESIZE
            imgDilate = Processamento(frame)
            checkVaga(imgDilate, frame)
            q.put(frame)
        else:
            break

def Display():
    while True:
        if q.empty() != True:
            frame = q.get()
            cv2.imshow('Estacionamento', frame)
            # cv2.imshow('EstacionamentoBlur', imgBlur)
            # cv2.imshow('EstacionamentoThreshold', imgThreshold)
            # cv2.imshow('EstacionamentoMedian', imgMedian)
            # cv2.imshow('EstacionamentoDilate',imgDilate)
            if cv2.waitKey(40) & 0xFF == ord('q'):
                break
        else:
            cv2.waitKey(40*10)

if __name__ == '__main__':
    threads=[]

    p1 = threading.Thread(target=Receive)
    p2 = threading.Thread(target=Display)
    threads.append(p1)
    threads.append(p2)
    p1.start()
    p2.start()
    p2.join()
    p1.join()
