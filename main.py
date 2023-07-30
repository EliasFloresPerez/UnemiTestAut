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

    """
    **Función**: Manda a analizar la imagen

    - **imagen**: Imagen a analizar.
    - **diccionario**: Diccionario en Texto que contiene la cantidad de preguntas y elecciones de esta manera
    
    ```
    {
        "#Preguntas": "20",
        "#Elecciones": "4"
    }
    ```

    - Retorna un diccionario con las elecciones seleccionadas por el estudiante en un arreglo de tamaño N en un rango que comienza desde 0 hasta elecciones-1
    - En caso de error Devuelve un diccionario con la clave "Error" y el valor del error
    """

    # Leer los datos de la imagen en memoria
    image_data = await image.read()

    # Convertir los datos en un arreglo de bytes
    nparr = np.frombuffer(image_data, np.uint8)

    # Decodificar el arreglo de bytes en una imagen utilizando OpenCV
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    

    try:
        diccionario = json.loads(diccionario)
        preguntas = int(diccionario["#Preguntas"])
        eleccion  = int(diccionario["#Elecciones"])
    except:
        return {"Error":"No se pudo cargar el diccionario"}

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

    """
    **Función**: Manda a analizar la imagen

    - **imagen**: Imagen a analizar.
    - **diccionario**: Diccionario en Texto que contiene la cantidad de preguntas y elecciones de esta manera

    ```
    {
        "#Preguntas": "20",
        "#Elecciones": "4"
    }
    ```
    - Retorna un diccionario con las elecciones seleccionadas por el estudiante en un arreglo de tamaño N en un rango que comienza desde 0 hasta elecciones-,
      Ademas d guardar las imagenes en la carpeta Archivos /Archivos/Imagen_N.jpg donde N es el numero de imagenes que van desde  0 a 10 
    - En caso de error Devuelve un diccionario con la clave "Error" y el valor del error

    """
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
    respuesta  = diccionario["Respuestas"]
    
    #Respuestas es esto y lo quiero a arreglo : 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
    try:
        if respuesta != "":
            respuesta = respuesta.split(",")

    except:
        respuesta = None

    datos = AnalizadorImagenes().Iniciar(img,preguntas,eleccion,respuestas=respuesta)
    
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


    """
        Función: Obtener los datos de un profesor al ingresar al aplicativo

        - **user**: Usuario del profesor
        - **password**: Contraseña del profesor
        - Retorna un diccionario con su token y sus materias con este formato
        ```
        {
            "Token": "Token del profesor",
            "Nombre de la Materia": {
                "id": "id de la materia",
                "assignments": {
                    "Nombre de la tarea": "id de la tarea"
                }
            },
            ...
        }
        ```
        - En caso de error Devuelve un diccionario con la clave "Error" y el valor del error


    """
    #link = "https://vaquitamoodle.raulgarcia.dev/"
    try:
        token = login(user, password, link)
    except:
        return {"Error":"Contraseña o usuario incorrecto"}
    
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
    """
        **Función**: Enviar las notas de los estudiantes al moodle

        - **token**: Token del profesor
        - **data**: Lista de diccionarios en Texto que contiene las notas de los estudiantes de esta manera

        ```
        [
            {
                "assignmentid": "id de la tarea",
                "userid": "id del estudiante",
                "nota": "nota del estudiante"
            }, 
            ...
        ]
        ```
        - Retorna un diccionario con la clave "Estado" y el valor "OK 200"
        - En caso de error Devuelve un diccionario con la clave "Error" y el valor del error (Aun no implementado)
    """
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
    
    """
        **Función**: Obtener las hojas de PDF para los estudiantes de una materia y lo envia al correo del profesor

        - **token**: Token del profesor
        - **id_examen**: id de la tarea
        - **course_id**: id de la materia
        - **tutor**: Nombre del profesor
        - **NombreMateria**: Nombre de la materia
        - **preguntas**: Cantidad de preguntas
        - **eleccion**: Cantidad de elecciones
        - **correo**: Correo del profesor
        
        - Retorna un diccionario con la clave "Estado" y el valor "ok"
        - En caso de error Devuelve un diccionario con la clave "Error" y el valor del error
    """

    try:
        int(id_examen)
        int(course_id)
        int(preguntas)
        int(eleccion)
    except:
        return {"Error":"id_examen, course_id, preguntas o eleccion no es un numero"}

    try:
        estudiantes = getEstudiantes(token, int(course_id), link)
    except:
        return {"Error":"Token Error o Course_id Error"}
    
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
    
    return {"Estado":"ok"}

