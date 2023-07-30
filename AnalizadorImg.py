import cv2
import numpy as np
import utlis as utlis
from PIL import Image
import json


Data = {
    "Imagen":       None,
    "ImagenGris":   None,
    "ImnagenSombra":None,
    "ImagenCanny":  None,
    "Contornos":    None,
    "ContornoBig":  None,
    "ImagenCuadricula":[],
    "ImagenAnswers":[],
    "ImagenFinal":  None,
    "Informacion":{
        "#Preguntas":None,
        "#Elecciones":None,
        "RespuestasTest":None,
        "RespuestasUser":None,
        "Nota":None
    }
}


DataJson = {
    "Respuestas":None,
    "#Preguntas":None,
    "#Elecciones":None,
    "Nota" : None
}

"""
def analizar_qr(imagen):
    
    # Decodificar el código QR
    qr_codes = decode(imagen)
    
    if qr_codes:
        # Extraer el contenido del código QR
        contenido_qr = qr_codes[0].data.decode('utf-8')
        return contenido_qr
    else:
        return None
"""

class QuitarSombras():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    

    def map(self,x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def highPassFilter(self,kSize,img):
        
        if not kSize%2:
            kSize +=1
            
        kernel = np.ones((kSize,kSize),np.float32)/(kSize*kSize)

        filtered = cv2.filter2D(img,-1,kernel)

        filtered = img.astype('float32') - filtered.astype('float32')
        filtered = filtered + 127*np.ones(img.shape, np.uint8)

        filtered = filtered.astype('uint8')

        img = filtered

        return img
        

        
    def blackPointSelect(self,img,blackPoint):

        img = img.astype('int32')

        img = self.map(img, blackPoint, 255, 0, 255)

        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_TOZERO)

        img = img.astype('uint8')
        
        return img

    def whitePointSelect(self,img,whitePoint):
        
        _,img = cv2.threshold(img, whitePoint, 255, cv2.THRESH_TRUNC)

        img = img.astype('int32')
        img = self.map(img, 0, whitePoint, 0, 255)
        img = img.astype('uint8')

        return img
        
        
    #200 110
    #150 150    
    def Ejecutar(self,img,b = 200,w =110):
        blackPoint = b
        whitePoint = w
        
        img = self.highPassFilter(300, img)
        img = self.whitePointSelect(img,whitePoint)
        img = self.blackPointSelect(img,blackPoint)

        return img

class AnalizadorImagenes():
    heightImg = 700
    widthImg  = 700

    def __init__(self):
        pass
    
    

    def Iniciar(self, img,preguntas,elecciones,respuestas = None):
        
        
        
        newData = Data.copy()
        #Borrar
        #img = cv2.imread(img)

        

        
        newData["Informacion"]["#Preguntas"] = preguntas
        newData["Informacion"]["#Elecciones"] = elecciones
        
        

        
        newData["Imagen"] = img
        newData["Informacion"]["RespuestasTest"] = respuestas

        try:
            newData["ImagenCuadricula"] = []
            newData["ImagenAnswers"] = []
            self.Convertir_imagenes(newData)
            self.Contornos(newData)

        except :
            
            #Proceso para testing
            newData  = {
                "Error":"No se pudo analizar la imagen",
            }
        
        return newData
   

    def Convertir_imagenes(self,Datos):
        


        #Cambiamos el tamaño de la foto con el tamaño predefinido
        Datos["Imagen"] = cv2.resize(Datos["Imagen"], (self.widthImg, self.heightImg))

        Datos["ImnagenSombra"]  = QuitarSombras().Ejecutar(Datos["Imagen"])
        #Datos["ImnagenSombra"]  = QuitarSombras().Ejecutar(Datos["Imagen"],200,110)
        Datos["ImnagenSombra"] = cv2.resize(Datos["ImnagenSombra"], (self.widthImg, self.heightImg))
        #Datos["ImnagenSombra"] = Datos["Imagen"].copy()
        #Copiar la imagen para el final
        Datos["ImagenFinal"] = Datos["Imagen"].copy()


        #Imagen en negro para debugguiar
        imgBlank = np.zeros((self.heightImg,self.widthImg, 3), np.uint8)

        #En escalas de grises
        Datos["ImagenGris"] = cv2.cvtColor(Datos["Imagen"], cv2.COLOR_BGR2GRAY)
        
        #En Blur Gaussian
        imgBlur = cv2.GaussianBlur(Datos["ImagenGris"], (5, 5), 1)

        #Aplicar Canny
        Datos["ImagenCanny"] = cv2.Canny(imgBlur,10,70)

        return Datos
    


    def Contornos(self,Datos):
        #Encontrar los contornos
        #Buscaremos 1 o  2  rectangulos

        Datos["Contornos"] =   Datos["Imagen"].copy()
        Datos["ContornoBig"] = Datos["Imagen"].copy()

        #Encuentra los contornos
        contours, hierarchy = cv2.findContours(Datos["ImagenCanny"], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        #Dibuja en ellos de color verde para verlos
        cv2.drawContours(Datos["Contornos"], contours, -1, (0, 255, 0), 10)

        #Sacamos los rectangulos que encontremos y filtramos
        rectContornos = utlis.rectContour(contours)
        
        #Analizamos cuantos rectangulos hay y por cada uno de ellos los analizamos
        rectCordenadas = []
        for rect in rectContornos:
            #print("Area ",cv2.contourArea(rect))
            rectCordenadas.append(utlis.getCornerPoints(rect))
        
        
        #Ordenamos los rectangulos de mayor a menor por su area los dos mas grandes seran
        #El conjunto de preguntas
        rectangulos_ordenados = sorted(rectCordenadas, key=lambda rect: cv2.contourArea(rect), reverse=True)
        

        #Separamos la data en grupos de 10 preguntas y el restante
        if Datos["Informacion"]["#Preguntas"] <= 10:

            rectangulos_ordenados = rectangulos_ordenados[:1]
        else:
            
            rectangulos_ordenados = rectangulos_ordenados[:2]
           
            #Ordenamos los rectangulos de izquierda a derecha
            if rectangulos_ordenados[0][0][0][0] > rectangulos_ordenados[1][0][0][0] :
                    rectangulos_ordenados[0] , rectangulos_ordenados[1] = rectangulos_ordenados[1]  ,rectangulos_ordenados[0] 
        

        valor_iteracion = 10  # Valor predeterminado a pasar en cada iteración
        rectAnalizado = []  # Lista para almacenar los resultados
        preguntas_restantes = Datos["Informacion"]["#Preguntas"]

        
        for i in rectangulos_ordenados:
            if preguntas_restantes <= valor_iteracion:
                valor_iteracion = preguntas_restantes

            rectAnalizado.append(self.Analizar_Rectangulo(i, valor_iteracion,Datos))
            preguntas_restantes -= valor_iteracion

        self.Evaluar_rectangulos(Datos,rectAnalizado)
        

    


    def Analizar_Rectangulo(self,biggestPoints,preguntas,Datos):
            #Reordenar para aplicar transformacion
            #print("Arreglo : ",biggestPoints)
            biggestPoints=utlis.reorder(biggestPoints) 
            
            #Pintar los contorno de ese rectangulo
            cv2.drawContours(Datos["ContornoBig"], biggestPoints, -1, (0, 255, 0), 20)

            #Transformar los puntos para la transformacion a una perspectiva tipo matrix
            pts1 = np.float32(biggestPoints) # PREPARE POINTS FOR WARP
            pts2 = np.float32([[0, 0],[self.widthImg, 0], [0, self.heightImg],[self.widthImg, self.heightImg]]) # PREPARE POINTS FOR WARP
            matrix = cv2.getPerspectiveTransform(pts1, pts2) # GET TRANSFORMATION MATRIX
            
            imgWarpColored = cv2.warpPerspective(Datos["ImnagenSombra"], matrix, (self.widthImg, self.heightImg)) # APPLY WARP PERSPECTIVE

            # Aplicar THRESHOLD
            #Convertir a  GRAYSCALE
            imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(imgWarpGray, (3, 3), 3) 
            # Aplicar Tresh INVERSE
            imgThresh = cv2.threshold(blurred, 170, 255,cv2.THRESH_BINARY_INV )[1]
            
            boxes = utlis.splitBoxes(imgThresh,preguntas,Datos["Informacion"]["#Elecciones"]) 
            
            countR=0
            countC=0
            myPixelVal = np.zeros((preguntas,Datos["Informacion"]["#Elecciones"])) # TO STORE THE NON ZERO VALUES OF EACH BOX
            
            for image in boxes:
                
                totalPixels = cv2.countNonZero(image)
                myPixelVal[countR][countC]= totalPixels
                countC += 1
                if (countC==Datos["Informacion"]["#Elecciones"]):countC=0;countR +=1
            

            #cv2.imshow("Imagen", imgThresh)
            #cv2.waitKey(0)
            
            
            return {
                "ValorPixel":myPixelVal,
                "ImagenThesh":imgThresh,
                "ImagenColor":imgWarpColored,
                "Punto1":pts1,
                "Punto2":pts2,
                "#Preguntas":preguntas
            }  



    def Evaluar_rectangulos(self,Datos,rectAnalizados):
        respuestas = Datos["Informacion"]["RespuestasTest"]
        nElecciones = Datos["Informacion"]["#Elecciones"]
        TotalRespuestasUser = []
        TotalAciertosUser = []
        
        for Dict in rectAnalizados:
            RespuestasUser = self.Calcular_Respuestas(Dict["ValorPixel"],Dict["#Preguntas"])
            TotalRespuestasUser.extend(RespuestasUser)
            
            AciertosUser = None
            if respuestas != None:
                AciertosUser = self.Calcular_Aciertos(RespuestasUser,respuestas,Dict["#Preguntas"])
                TotalAciertosUser.extend(AciertosUser)
            
            Datos["ImagenAnswers"].append(self.Agregador_visual(Dict,RespuestasUser,nElecciones,AciertosUser,respuestas,Datos))

            Datos["ImagenCuadricula"].append(Dict["ImagenThesh"])

        Datos["Informacion"]["RespuestasUser"] = TotalRespuestasUser
        #Calculamos la nota final
        if respuestas != None:
            Datos["Informacion"]["Nota"] = (sum(TotalAciertosUser)/Datos["Informacion"]["#Preguntas"])*100
        
        


               
    #Mostrar las respuestas elegidas si son error o su respuesta correcta
    def Agregador_visual(self,Dict,RespuestasUser,elecciones,AciertosUser,respuestas,Datos):
        
        preguntas = Dict["#Preguntas"]

        utlis.showAnswers(Dict["ImagenColor"],RespuestasUser,preguntas,elecciones,AciertosUser,respuestas) # DRAW DETECTED ANSWERS
        utlis.drawGrid(Dict["ImagenColor"],preguntas,elecciones) # DRAW GRID
        imgRawDrawings = np.zeros_like(Dict["ImagenColor"]) # NEW BLANK IMAGE WITH WARP IMAGE SIZE

        #Lo mismo pero la la imagen final
        utlis.showAnswers(imgRawDrawings,RespuestasUser,preguntas,elecciones,AciertosUser,respuestas) # DRAW ON NEW IMAGE
        invMatrix = cv2.getPerspectiveTransform(Dict["Punto2"], Dict["Punto1"]) # INVERSE TRANSFORMATION MATRIX
        imgInvWarp = cv2.warpPerspective(imgRawDrawings, invMatrix, (self.widthImg,self.heightImg)) # INV IMAGE WARP

        # Agregar a la imagen final
        Datos["ImagenFinal"] = cv2.addWeighted(Datos["ImagenFinal"], 1, imgInvWarp, 1,0)
        #self.imgFinal = cv2.addWeighted(self.imgFinal, 1, imgInvWarp, 1,0)}

        return Dict["ImagenColor"]  


    def Calcular_Respuestas(self,MatrizPixel,preguntas):
        #Agragamos como respuestas a los que tienen mas pixeles en su linea
        
        RespuestaUser=[]
        

        for x in range (0,preguntas):
            arr = MatrizPixel[x]
            RespuestaUsuarioVal = np.where(arr == np.amax(arr))
            RespuestaUser.append(RespuestaUsuarioVal[0][0])
        
        return RespuestaUser


    def Calcular_Aciertos(self,RespuestaUser,respuestas,preguntas):
        AciertosUser =[]
       
        #comparamos con el arreglo de respuestas
        for x in range(0,preguntas):
            if respuestas[x] == RespuestaUser[x]:

                AciertosUser.append(1)

            else:
                AciertosUser.append(0)
    
        
        
        return AciertosUser

    def Retornar_Datos(self,Datos):
        response = DataJson.copy()

        response["Respuestas"] = Datos["Informacion"]["RespuestasUser"]
        response["#Preguntas"] = Datos["Informacion"]["#Preguntas"]
        response["#Elecciones"] = Datos["Informacion"]["#Elecciones"]
        response["Nota"] = Datos["Informacion"]["Nota"]
        #response["DatosQR"] = Datos["Informacion"]["DatosQR"]
        
        #cv2.imshow("Imagen", Datos["ImagenFinal"])
        #cv2.imshow("Imagen", Datos["ImagenCuadricula"][1])
        #cv2.waitKey(0)
        return response

    
#a = AnalizadorImagenes().Iniciar("Prueba.png",[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
#print(AnalizadorImagenes().Retornar_Datos(a))




