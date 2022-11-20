import cv2
import pickle

ARQ_POS="PosEstacionamento"
alt,compr=45,25

try:
    with open(ARQ_POS, 'rb') as arq:
        posList=pickle.load(arq)

except:
    posList=[]

rtsp_url=r'rtsp://admin:SSYRMI@192.162.254.100:554/cam/realmonitor?channel=1&subtype=0'
#rtsp_url=r'sample.mp4'

camera=cv2.VideoCapture(rtsp_url)

def mouseClick(events,x,y,flags,params):
    if events ==cv2.EVENT_LBUTTONDOWN:
        posList.append((x,y))
        print('\n',posList)
    if events == cv2.EVENT_RBUTTONDOWN:
        if len(posList)>1:
            for i,pos in enumerate(posList):
                if i>0: # Somente a partir do índice 1 (2ª elemento) existirá uma pos_ant
                    pos_ant=posList[i-1]
                if i%2!=0:
                    if pos_ant[0]<x<pos[0] and pos_ant[1]<y<pos[1]:
                        posList.pop(i)
                        posList.pop(i - 1)

                        print('\nTRUE')
                        print(posList)

                    else:
                        print('\nFALSE')
                    print('i: ',i,' x: ',x,' y: ',y,' pos: ', pos, ' pos_ant: ', pos_ant)


    with open(ARQ_POS, 'wb') as arq:
        pickle.dump(posList,arq)

if camera.isOpened():
    validacao,frame=camera.read()

    object_detector=cv2.createBackgroundSubtractorMOG2()

    while True:
        validacao, frame = camera.read()
        if not validacao:
            print('validacao false')
            camera.release()
            camera = cv2.VideoCapture(rtsp_url)
            _, frame = camera.read()
        #frame = cv2.flip(frame, 0)
        frame=cv2.resize(frame,(854,480))

        if len(posList)>1:
            for i,pos in enumerate(posList):
                if i>0:
                    pos_ant=posList[i-1]
                if i%2!=0:
                    cv2.rectangle(frame, pos_ant, pos, (0, 255, 0), 2)
        ###mask=object_detector.apply(frame)
        ###cv2.imshow("Mask",mask)

        cv2.imshow("Camera da Sala",frame)
        cv2.setMouseCallback("Camera da Sala",mouseClick)

        if cv2.waitKey(40) & 0xFF == ord('q'):
            break
        cv2.imwrite("print.png",frame)

camera.release()
cv2.destroyAllWindows()