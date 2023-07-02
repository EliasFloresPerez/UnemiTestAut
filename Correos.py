import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def enviar_correo(destinatario,
                asunto = 'HOJAS DE EXAMENES PDF',
                mensaje = 'Aqui se encuentran las hojas de examen de los estudiantes',
                remitente = 'testcorreomoodle@gmail.com',
                contraseña = 'cwnqgtfzksyahwwq',
                archivo_adjunto = './PDF/Cuestionarios.pdf'):
    

    # Crear objeto MIME para el correo
    correo = MIMEMultipart()
    correo['From'] = remitente
    correo['To'] = destinatario
    correo['Subject'] = asunto

    # Agregar el mensaje al correo
    cuerpo_correo = MIMEText(mensaje, 'plain')
    correo.attach(cuerpo_correo)

    # Agregar el archivo adjunto
    adjunto = open(archivo_adjunto, 'rb')

    # Crear un objeto MIME base
    objeto_adjunto = MIMEBase('application', 'octet-stream')
    objeto_adjunto.set_payload(adjunto.read())
    adjunto.close()

    # Codificar el archivo adjunto en base64
    encoders.encode_base64(objeto_adjunto)

    # Agregar encabezados al objeto adjunto
    objeto_adjunto.add_header('Content-Disposition', 'attachment', filename="HojasDeExamen.pdf")

    # Agregar el objeto adjunto al correo
    correo.attach(objeto_adjunto)

    # Conectar al servidor SMTP y enviar el correo
    servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)  # Utiliza el servidor SMTP correspondiente
    servidor_smtp.starttls()
    servidor_smtp.login(remitente, contraseña)
    servidor_smtp.send_message(correo)
    servidor_smtp.quit()



#enviar_correo('rgarciac5@unemi.edu.ec')
