import cv2
import numpy as np



#Reegordena los puntos de la imagen
def reorder(myPoints):

    myPoints = myPoints.reshape((4, 2)) # REMOVE EXTRA BRACKET
    #print(myPoints)
    myPointsNew = np.zeros((4, 1, 2), np.int32) # NEW MATRIX WITH ARRANGED POINTS
    add = myPoints.sum(1)
    #print(add)
    #print(np.argmax(add))
    myPointsNew[0] = myPoints[np.argmin(add)]  #[0,0]
    myPointsNew[3] =myPoints[np.argmax(add)]   #[w,h]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] =myPoints[np.argmin(diff)]  #[w,0]
    myPointsNew[2] = myPoints[np.argmax(diff)] #[h,0]

    return myPointsNew

#Nos devulve el contorno del rectangulo en un array
def rectContour(contours):

    rectCon = []
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 50:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if len(approx) == 4:
                rectCon.append(i)
    rectCon = sorted(rectCon, key=cv2.contourArea,reverse=True)
    #print(len(rectCon))
    return rectCon

#Nos devuelve los puntos del poligono
def getCornerPoints(cont):
    peri = cv2.arcLength(cont, True) # LENGTH OF CONTOUR
    approx = cv2.approxPolyDP(cont, 0.02 * peri, True) # APPROXIMATE THE POLY TO GET CORNER POINTS
    return approx

#Caja separada por su cuadrante de preguntas y elecciones
def splitBoxes(img,questions=5,choices=10):
    rows = np.vsplit(img,questions)
    boxes=[]
    for r in rows:
        cols= np.hsplit(r,choices)
        for box in cols:
            boxes.append(box)
    return boxes

#Dibujas las gridas de las preguntas y elecciones
def drawGrid(img,questions=10,choices=4):
    secW = int(img.shape[1]/choices)
    secH = int(img.shape[0]/questions)
    for i in range (0,10):
        pt1 = (0,secH*i)
        pt2 = (img.shape[1],secH*i)
        pt3 = (secW * i, 0)
        pt4 = (secW*i,img.shape[0])
        cv2.line(img, pt1, pt2, (255, 255, 0),2)
        cv2.line(img, pt3, pt4, (255, 255, 0),2)

    return img

#Nos permite dibujar las respuestas seleccionadas
def showAnswers(img,myIndex,questions=10,choices=5,grading = None,ans = None):
    secW = int(img.shape[1]/choices)
    secH = int(img.shape[0]/questions)
     
    for x in range(0,questions):
         
        myAns= myIndex[x]
        cX = (myAns * secW) + secW // 2
        cY = (x * secH) + secH // 2


        if grading != None :

            if grading[x] == 0:
            
                # Respuesta correcta
                myColor = (0, 255, 0)
                cv2.circle(img,((ans[x] * secW)+secW//2, (x * secH)+secH//2),20,myColor,cv2.FILLED)

        myColor = (0, 77, 255)
        cv2.circle(img, (cX, cY), 25, myColor, cv2.FILLED)
        
