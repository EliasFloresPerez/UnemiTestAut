

import qrcode
from fpdf import FPDF
from PIL import Image
import os

"""
    Este archivo tiene la funcion de crear las hojas de pdf segun los requisitos del proyecto
"""
"""
datoS = [
    {
        "nombre": "Elias Flores xd",
        "userid":"6",
        "materia": "Desarrollo Web",
        "tutor": "Ronald Henry Diaz",
        "tareaid": "1",
        "#Preguntas":"20",
        "#Elecciones":"4",
    },
    {
        "nombre": "Kelly Cruz",
        "userid":"7",
        "materia": "Desarrollo Web",
        "tutor": "Ronald Henry Diaz",
        "tareaid": "1",
        "#Preguntas":"20",
        "#Elecciones":"4",
    },
]
"""


class CrearPdf():

    def __init__(self):
        self.pdf = FPDF(orientation='P', unit='mm', format='A4')
        self.pdf.set_font("Arial", size=12)

    def CrearHoja(self, datos):

        self.pdf.add_page()
        # Ponemos la imagen de la
        self.pdf.image("PDF/LogoUnemi.png", x=(210/2) -
                       25, y=5, w=50, h=20, type="PNG")

        # Creamos la tabla de datos
        self.pdf.set_font("Arial", size=12)
        self.CrearTabla(datos)

        # Colocamos el QR
        self.Poner_Qr(datos)

        # Colocamos el titulo
        self.pdf.set_font("Arial", size=12)
        self.pdf.set_xy(20, 60)
        self.pdf.text(
            20, 85, "Rellene la respuesta correcta en su totalidad, evite seleccionar dos respuestas.")

        # Colocamos el fotter
        self.pdf.text(
            (210/2) - 60, 280, "Universidad Estatal de Milagro Todos los Derechos Reservados *")

        # Colocamos las preguntas

        preguntas = int(datos["#Preguntas"])
        elecciones = int(datos["#Elecciones"])
        if preguntas > 10:
            self.Cololcar_Preguntas(10, elecciones, 20, 105)

            self.Cololcar_Preguntas(preguntas - 10, elecciones, 111, 105, 10)
        else:
            self.Cololcar_Preguntas(
                preguntas, elecciones, (210/2)-5 - (17 * elecciones + 3)/2, 105)

    def CrearTabla(self, datos):
        # Crear Tabla
        tam_w = 30
        tam_h = 6
        tam_w2 = 100

        self.pdf.set_xy(20, 40)

        self.pdf.cell(tam_w, tam_h, 'Materia ', border=1, ln=0)
        self.pdf.multi_cell(
            tam_w2, tam_h, datos["materia"], border=1, align='C')

        self.pdf.set_x(20)
        self.pdf.cell(tam_w, tam_h, 'Estudiante ', border=1)
        self.pdf.multi_cell(
            tam_w2, tam_h, datos["nombre"], border=1, align='C')

        self.pdf.set_x(20)
        self.pdf.cell(tam_w, tam_h, 'Tutor ', border=1)
        self.pdf.multi_cell(tam_w2, tam_h, datos["tutor"], border=1, align='C')

        self.pdf.set_x(20)
        self.pdf.cell(tam_w, tam_h, 'Semestre ', border=1)
        self.pdf.cell(35, tam_h, '', border=1, align='C')
        self.pdf.cell(tam_w, tam_h, 'Curso ', border=1)
        self.pdf.multi_cell(35, tam_h, '', border=1, align='C')

        self.pdf.set_x(20)
        self.pdf.cell(tam_w, tam_h, 'Fecha ', border=1)
        self.pdf.multi_cell(tam_w2, tam_h, '', border=1, align='C')

    def Poner_Qr(self, datos):

        DataQr = {
            "userid": datos["userid"],
            "tareaid": datos["tareaid"],
            "Nombre :": datos["nombre"],
            "#Preguntas": datos["#Preguntas"],
            "#Elecciones": datos["#Elecciones"],
        }
        print(DataQr)

        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=4, border=1)
        qr.add_data(DataQr)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save("./PDF/qrTemporal_{}.png".format(DataQr["userid"]))

        self.pdf.image(
            "./PDF/qrTemporal_{}.png".format(DataQr["userid"]), x=164, y=39, w=32, h=32, type="PNG")

        os.remove("./PDF/qrTemporal_{}.png".format(DataQr["userid"]))

    def Cololcar_Preguntas(self, preguntas, elecciones, pos_x, pos_y, aumento=0):
        self.pdf.set_font("Arial", size=15)

        # Creamos elipse con su texto centrado dada una posicion
        def Crear_elipse(x, y, w, h, Texto):
            self.pdf.ellipse(x, y, w, h, style='D')
            text_width = self.pdf.get_string_width(Texto)
            text_height = self.pdf.font_size

            text_x = x + (w - text_width) / 2
            text_y = y + (h - text_height) / 2

            self.pdf.text(text_x, text_y + 4, Texto)

        Letras = ['A', 'B', 'C', 'D', 'E']

        for i in range(preguntas):

            self.pdf.text(pos_x, pos_y + 10 + (13 * i),
                          "{}.".format(i+1 + aumento))

            for j in range(elecciones):

                Crear_elipse(pos_x + 11 + (17 * j), pos_y +
                             3 + (13 * i), 14, 10, Letras[j])

        self.pdf.rect(pos_x + 8, pos_y, 17 *
                      elecciones + 3, 13 * preguntas + 3)

        pass

    def Guardar(self, nombre="Cuestionarios"):
        self.pdf.output("PDF/{}.pdf".format(nombre))
