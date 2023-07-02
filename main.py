from fastapi import FastAPI, UploadFile, File , Form ,Response
from fastapi.responses import FileResponse
import numpy as np
import cv2
import json
from AnalizadorImg import * 
from fastapi.staticfiles import StaticFiles

from MoodleConector import *
from PDF.CreadorPDF import *
from Correos import *

import os
app = FastAPI()

def codificar_json(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


#Funcion que recibe una imagen y la analiza
@app.post("/Analizar/")
async def upload_image(image: UploadFile = File(...),diccionario: str =  Form(default=None)):
    # Leer los datos de la imagen en memoria
    image_data = await image.read()

    # Convertir los datos en un arreglo de bytes
    nparr = np.frombuffer(image_data, np.uint8)

    # Decodificar el arreglo de bytes en una imagen utilizando OpenCV
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    

    
    diccionario = json.loads(diccionario)
    preguntas = int(diccionario["#Preguntas"])
    eleccion  = int(diccionario["#Elecciones"])

    datos = AnalizadorImagenes().Iniciar(img,preguntas,eleccion)
    


    

    #Quiero saber si datos que es un diccionario tiene una clave llamada error
    if "Error" in datos:
        return datos
    
    datos = AnalizadorImagenes().Retornar_Datos(datos)
    
    # Convertir el diccionario a formato JSON
    json_data = json.dumps(datos, default=codificar_json)
    
    return json_data


#Al ser esta una funcion para angular puedo guardar los archivos en la carpeta correspondiente
def GuardarImagenes(dict):

    contador = 0
    for i in dict:
        # Guardar la imagen en formato JPG

        if isinstance(dict[i], list):
            for j in dict[i]:
                cv2.imwrite('./Archivos/Imagen_{}.jpg'.format(contador), j)
                contador += 1
        else:
            try:
                cv2.imwrite('./Archivos/Imagen_{}.jpg'.format(contador), dict[i])
                contador += 1
            except:
                pass
        

#Segundo analizar para la aplicacion en angular
@app.post("/Analizar2/")
async def upload_image(image: UploadFile = File(...), diccionario: str =  Form(default=None)):
    # Leer los datos de la imagen en memoria
    image_data = await image.read()

    # Convertir los datos en un arreglo de bytes
    nparr = np.frombuffer(image_data, np.uint8)

    # Decodificar el arreglo de bytes en una imagen utilizando OpenCV
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    diccionario = json.loads(diccionario)
    #arreglo   = diccionario["Respuesta"]
    preguntas = int(diccionario["#Preguntas"])
    eleccion  = int(diccionario["#Elecciones"])

    
    datos = AnalizadorImagenes().Iniciar(img,preguntas,eleccion)
    
    #Quiero saber si datos que es un diccionario tiene una clave llamada error
    if "Error" in datos:
        return datos
    
    #Convirtamos los arreglos numpy a imagenes binarias
    
    GuardarImagenes(datos)
    
    datos = AnalizadorImagenes().Retornar_Datos(datos)
    
    # Convertir el diccionario a formato JSON
    json_data = json.dumps(datos, default=codificar_json)

    return json_data

#Para recuperar las imagenes de la carpeta Archivos
app.mount("/Archivos", StaticFiles(directory="Archivos"), name="Archivos")


#Api para devolver los datos de moodle del profesor
@app.post("/Moodle/Ingresar")
def Obtener_Datos_Moodle(user: str =  Form(...), password: str =  Form(...)):

    #link = "https://vaquitamoodle.raulgarcia.dev/"
    token = login(user, password, link)
    userid = getUserId(token,user, link)


    arreglo = obtener_materias_del_profesor(link, token, userid)
    
    diccionario = {
        "Token": token
    }
    
    for i in arreglo:
        

        datos = getAssignments(token, i['id'], link)
        
        diccionario[i['fullname']] = {
            "id": i['id'],
            "assignments": {}
        }
        for j in datos['courses'][0]['assignments']:
            diccionario[i['fullname']]["assignments"][j['name']] = str(j['id'])

    # Aquí se encuentra fuera del bucle for
    return diccionario


#Permite enviar las notas de los estudiante al moodle
@app.post("/Moodle/setNotas")
def Enviar_Notas(token: str =  Form(...),data : str =  Form(...)):
    data = json.loads(data)

    for i in data:

        setNotas(token,i["assignmentid"],i["userid"],i["nota"],link)

    return {"Estado":"OK 200"}




#Aqui sera para obtener las hojas de words para los estudiantes.
@app.post("/Moodle/getHojasPDF")
def Obtener_HojasPDF(token : str =  Form(...) , 
                    id_examen: str =  Form(...),
                    course_id: str =  Form(...), 
                    tutor : str =  Form(...) ,
                    NombreMateria : str =  Form(...),
                    preguntas : str =  Form(...) ,
                    eleccion : str =  Form(...) ,
                    correo : str =  Form(...) ):
    
    estudiantes = getEstudiantes(token, int(course_id), link)
    diccionario = []

    for i in estudiantes:
        diccionario.append({
        "nombre": i["fullname"],
        "userid":i["id"],
        "materia": NombreMateria,
        "tutor": tutor,
        "tareaid": int(id_examen),
        "#Preguntas":int(preguntas),
        "#Elecciones":int(eleccion),
    })

    print(estudiantes)    
    obj = CrearPdf()

    for i in diccionario:
        obj.CrearHoja(i)
    
    obj.Guardar()

    file_path = "PDF/Cuestionarios.pdf"

    #Enviamos el correo

    enviar_correo(correo)
    

    # Devolver el archivo PDF como respuesta
    return {"ok":"ok"}

