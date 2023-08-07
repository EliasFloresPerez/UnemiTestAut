import requests


"""
    Este archivo tiene todos los microservicios que permiten la conexion con moodle
    Ingresar y recoger las materias con sus tareas 
    Recoger estudiantes de un curso
    Enviar notas a los estudiantes 
"""

link = "https://vaquitamoodle.raulgarcia.dev/"

#2737e7ca3fe524f64e7733212e2f6c18


#Ingresa a moodle y devuelve el token
def login(username, password ,link):
    url = link + '/login/token.php?service=moodle_mobile_app'
    data = {
        'moodlewsrestformat': 'json',
        'username': username,
        'password': password
    }

    res = requests.post(url, data=data).json()
    
    return res['token']

#Obtiene el id del usuario 
def getUserId(token, username,link):
    url = link + '/webservice/rest/server.php'
    data = {
        'moodlewsrestformat': 'json',
        'wstoken': token,
        'wsfunction': 'core_user_get_users_by_field',
        'field': 'username',
        'values[0]': username
    }
    res = requests.post(url, data=data).json()
    
    return res[0]['id']
   
#Ontiene las materias del profesor y las devolvemos en un arreglo
def obtener_materias_del_profesor(url,token,userid):
    url = link + '/webservice/rest/server.php'
    data = {
        'moodlewsrestformat': 'json',
        'wstoken': token,
        'wsfunction': 'core_enrol_get_users_courses',
        'userid': userid
    }
    res = requests.post(url, data=data).json()

    resultado = []
    for i in res:
        resultado.append({'id':i['id'],'fullname':i['fullname']})
    return resultado


#Obtener las tareas de la materia dado el id de la materia
def getAssignments(token, courseid , link):
    url = link + '/webservice/rest/server.php'
    data = {
        'moodlewsrestformat': 'json',
        'wstoken': token,
        'wsfunction': 'mod_assign_get_assignments',
        'courseids[0]': courseid
    }
    res = requests.post(url, data=data).json()

    return res

#Actualizamos la nota de un estudiante en una tarea(Examen)
def setNotas(token, assignmentid ,userid,nota, link):
    url = link +'/webservice/rest/server.php'

    data = {
        'moodlewsrestformat': 'json',
        'wstoken': token,
        'wsfunction': 'mod_assign_save_grade',
        'assignmentid': assignmentid,
        'userid':userid,
        'grade':nota,
        'attemptnumber':-1,
        'addattempt': 0,
        'workflowstate': 'graded',
        'applytoall': 0,

    }
    res = requests.post(url, data=data).json()
    return res


#Obtener Estudiantes del curso
def getEstudiantes(token, courseid , link):
    url = link + '/webservice/rest/server.php'
    data = {
        'moodlewsrestformat': 'json',
        'wstoken': token,
        'wsfunction': 'core_enrol_get_enrolled_users',
        'courseid': courseid
    }
    res = requests.post(url, data=data).json()

    #Guardamos los estudiantes
    resultado = []
    for i in res:
        if i['roles'][0]['shortname'] == 'student':
            resultado.append({'id':int(i['id']),'fullname':i['fullname']})

    return resultado









