# Made using code adapted from: https://www.youtube.com/watch?v=sVwWEoDa_uY&list=PLs3IFJPw3G9Jwaimh5yTKot1kV5zmzupt&index=6
# Made using code adapted from: https://github.com/The-Intrigued-Engineer/python_emails/blob/main/text_email.py
# Made using code adapted from: https://www.codeitbro.com/send-email-using-python/

from flask import Flask, request, jsonify
import pyrebase
from flask_cors import CORS
import smtplib
import ssl
import qrcode

############################################# DB and API configs############################################


api = Flask(__name__)
CORS(api)


firebaseConfig = {
    "apiKey": "AIzaSyAasBeKh-JrdSSllz2GEg8YEvlimoBR2J8",
    "authDomain": "eventos-tec-2d13f.firebaseapp.com",
    "databaseURL": "https://eventos-tec-2d13f-default-rtdb.firebaseio.com",
    "projectId": "eventos-tec-2d13f",
    "storageBucket": "eventos-tec-2d13f.appspot.com",
    "messagingSenderId": "684230874738",
    "appId": "1:684230874738:web:422955e4291d765ee194eb"
}

fb = pyrebase.initialize_app(firebaseConfig)
base = fb.database()

############################################# SMTP ############################################

def enviarCorreoATodos(message):
    try:
        estudiantes = base.child("estudiante").get()

        for estudiante in estudiantes.each():
            print(estudiante.val())
            enviarCorreo(estudiante.val()["correo"], message)
    except Exception as e:
        print(e)

def enviarCorreo(email_to, message):
    img = qrcode.make('Some data here')
    type(img)  # qrcode.image.pil.PilImage
    img.save("qrcode.png")

    smtp_port = 587                 # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    email_from = "bibliotecmail@gmail.com"
    # email_to = "xxxxxxxxxx@gmail.com"

    pswd = "pubrnylofjmuqmff"

    # Create context
    simple_email_context = ssl.create_default_context()

    try:
        # Connect to the server
        print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(email_from, pswd)
        print("Connected to server :-)")

        # Send the actual email
        print()
        print(f"Sending email to - {email_to}")
        TIE_server.sendmail(email_from, email_to, message)
        print(f"Email successfully sent to - {email_to}")

    # If there's an error, print it out
    except Exception as e:
        print(e)
        print("Error al enviar correo a: ", email_to)

    # Close the port
    finally:
        TIE_server.quit()


############################################# Asociaciones ############################################

# Esta función registra una asociación y su información en la DB
# Primero revisa si una con el mismo id ya existía
@api.route('/crear_asociacion', methods=["POST"])
def crear_asociacion():
    data = request.get_json()
    asociacion_id = data["asociacion_id"]
    nombre = data["nombre"]

    nueva_asociacion = {
        "asociacion_id": asociacion_id,
        "nombre": nombre
    }

    try:
        # Valida si la asociación ya fue registrada 
        asociacion = base.child("asociacion").get()
        for asociacion in asociacion.each():
            print(asociacion.val()["asociacion_id"])
            if (asociacion.val()["asociacion_id"] == asociacion_id):
                return jsonify({"message": "Esta asociacion ya ha sido registrada"})

        base.child("asociacion").push(nueva_asociacion)
        return jsonify({"message": "La asociacion se registró exitosamente"})

    except:
        return jsonify({"message": "Hubo un error al agregar la asociacion"})

# Esta función es un get de todas las asociaciones
@api.route('/get_asociaciones ', methods=["POST"])
def get_asociaciones():
    try:
        asociaciones = base.child("asociacion").get().val()
        lista_asociaciones = list(asociaciones.values())
        return jsonify(lista_asociaciones)

    except:
        return jsonify({"Hubo un error al consultar las asociaciones"})
    
# Esta función es un update de asociaciones
@api.route('/update_asociacion', methods=["POST"])
def update_asociacion():
    data = request.get_json()
    asociacion_id = data["asociacion_id"]
    nombre = data["nombre"]

    nueva_asociacion = {
        "asociacion_id": asociacion_id,
        "nombre": nombre
    }

    try:
        asociaciones = base.child("asociacion").get()
        for asociacion in asociaciones.each():
            if (asociacion.val()["asociacion_id"] == asociacion_id):
                if (asociacion_id != ""):
                    base.child("asociacion").child(asociacion.key()).update(
                        {"asociacion_id": asociacion_id})
                if (nombre != ""):
                    base.child("nombre").child(
                        asociacion.key()).update({"nombre": nombre})
                
                message = "Se actualizaron los datos de la asociacion: "
                message = message + str(nueva_asociacion["asociacion_id"])
                enviarCorreoATodos(message.encode('utf-8'))
                return jsonify({"message": "La asociacion se actualizó exitosamente"})

        return jsonify({"message": "La asociacion no existe"})

    except:
        return jsonify({"message": "Hubo un error al actualizar La asociacion"})

# Esta función elimina una asociación
@api.route('/delete_asociacion', methods=["POST"])
def delete_asociacion():
    data = request.get_json()
    asociacion_id = data["asociacion_id"]

    try:
        asociaciones = base.child("asociacion").get()
        for asociacion in asociaciones.each():
            if (asociacion.val()["asociacion_id"] == asociacion_id):
                base.child("asociacion").child(asociacion.key()).remove()
                return jsonify({"message": "La asociacion se eliminó exitosamente"})

        return jsonify({"message": "La asociacion no existe"})

    except:
        return jsonify({"message": "Hubo un error al eliminar La asociacion"})

############################################# Colaboradores ############################################

# Esta función registra a un colaboradorm, primero revisa si uno con este carnet ya existía
@api.route('/crear_colaborador', methods=["POST"])
def crear_colaborador():
    data = request.get_json()
    carnet = data["carnet"]
    nombre = data["nombre"]
    asociacion_id = data["asociacion_id"]
    es_organizador = data["es_organizador"]
    correo = data["correo"]
    contrasena = data["contrasena"]

    nuevo_colaborador = {
        "carnet": carnet,
        "nombre": nombre,
        "asociacion_id": asociacion_id,
        "es_organizador": es_organizador,
        "correo": correo,
        "contrasena": contrasena
    }

    try:
        # Validates if the student has already been registered
        colaboradores = base.child("colaborador").get()
        for colaborador in colaboradores.each():
            print(colaborador.val()["carnet"])
            if (colaborador.val()["carnet"] == carnet):
                return jsonify({"message": "Este colaborador ya ha sido registrado"})

        base.child("colaborador").push(nuevo_colaborador)
        return jsonify({"message": "El colaborador se registro exitosamente"})

    except:
        return jsonify({"message": "Hubo un error al agregar al colaborador"})

# Esta función es un get de los colaboradores
@api.route('/get_colaboradores', methods=["POST"])
def get_colaboradores():
    try:
        colaboradores = base.child("colaborador").get().val()
        lista_colaboradores = list(colaboradores.values())
        return jsonify(lista_colaboradores)

    except:
        return jsonify({"message": "Hubo un error al consultar los colaboradores"})

# Esta función actualiza la información de un colaborador
@api.route('/update_colaborador', methods=["POST"])
def update_colaborador():
    data = request.get_json()
    carnet = data["carnet"]
    nombre = data["nombre"]
    correo = data["correo"]
    asociacion_id = data["asociacion_id"]
    es_organizador = data["es_organizador"]

    nuevo_colaborador = {
        "carnet": carnet,
        "nombre": nombre,
        "correo": correo,
        "asociacion_id": asociacion_id,
        "es_organizador": es_organizador

    }

    try:
        colaboradores = base.child("colaborador").get()
        for colaborador in colaboradores.each():
            print(colaborador.val()["carnet"])
            if (colaborador.val()["carnet"] == carnet):
                if (nombre != ""):
                    base.child("colaborador").child(
                        colaborador.key()).update({"nombre": nombre})
                if (correo != ""):
                    base.child("colaborador").child(
                        colaborador.key()).update({"correo": correo})
                if (asociacion_id != ""):
                    base.child("colaborador").child(colaborador.key()).update(
                        {"asociacion_id": asociacion_id})
                if (es_organizador != ""):
                    base.child("colaborador").child(colaborador.key()).update(
                        {"es_organizador": es_organizador})
                
                return jsonify({"message": "El colaborador se editó exitosamente"})

        return jsonify({"message": "Este colaborador no se ha encontrado"})

    except:
        return jsonify({"message": "Hubo un error al editar al colaborador"})

# Esta función elimina a un colaborador
@api.route('/delete_colaborador', methods=["POST"])
def delete_colaborador():
    data = request.get_json()
    carnet = data["carnet"]

    try:
        colaboradores = base.child("colaborador").get()
        for colaborador in colaboradores.each():
            if (colaborador.val()["carnet"] == carnet):
                base.child("colaborador").child(colaborador.key()).remove()
                return jsonify({"message": "El colaborador se elimino exitosamente"})

        return jsonify({"message": "El colaborador no existe"})

    except:
        return jsonify({"message": "Hubo un error al eliminar al colaborador"})

# Esta función crea una asignación para un colaborador
@api.route('/asignar_colaborador', methods=["POST"])
def asignar_colaborador():
    data = request.get_json()
    carnet = data["carnet"]
    flag = data["flag"]
    evento_id = data["evento_id"]
    actividad_id = data["actividad_id"]

    if flag:
        nueva_asignacion = {
            "carnet": carnet,
            "evento_id": evento_id,
        }
    else: 
        nueva_asignacion = {
            "carnet": carnet,
            "evento_id": evento_id,
            "actividad_id": actividad_id
        }
    try:
        base.child("asignacion").push(nueva_asignacion)
        return jsonify({"message": "La asignacion asignacion se registro exitosamente"})

    except:
        return jsonify({"message": "Hubo un error al agregar la asignacion"})

############################################# Eventos ############################################

# Esta función crea un evento
@api.route('/crear_evento ', methods=["POST"])
def crear_evento():
    data = request.get_json()
    evento_id = data["evento_id"]
    nombre = data["nombre"]
    fecha_inicio = data["fecha_inicio"]
    fecha_fin = data["fecha_fin"]
    asociacion_id = data["asociacion_id"]
    capacidad = data["capacidad"]
    descripcion = data["descripcion"]


    correo = data["correo"]
    contrasena = data["contrasena"]

    nuevo_evento = {
        "data": data,
        "evento_id": evento_id,
        "nombre": nombre,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "asociacion_id": asociacion_id,
        "capacidad": capacidad,
        "descripcion": descripcion
    }

    try:
        # Validates if the event has already been registered
        eventos = base.child("evento").get()
        for evento in eventos.each():
            print(evento.val()["evento_id"])
            if (evento.val()["evento_id"] == evento_id):
                return jsonify({"message": "Este evento ya ha sido registrado"})

        base.child("evento").push(nuevo_evento)
        return jsonify({"message": "El evento se registro exitosamente"})

    except:
        return jsonify({"message": "Hubo un error al agregar al evento"})

# Esta función es un get de los eventos
@api.route('/get_eventos', methods=["POST"])
def get_eventos():
    try:
        eventos = base.child("evento").get().val()
        lista_eventos = list(eventos.values())
        return jsonify(lista_eventos)

    except:
        return jsonify({"message": "Hubo un error al consultar los eventos"})

# Esta función es un update de los eventos
@api.route('/update_evento', methods=["POST"])
def update_evento():
    data = request.get_json()
    evento_id = data["evento_id"]
    nombre = data["nombre"]
    fecha_inicio = data["fecha_inicio"]
    fecha_fin = data["fecha_fin"]
    asociacion_id = data["asociacion_id"]
    capacidad = data["capacidad"]
    descripcion = data["descripcion"]

    nuevo_evento = {
        "data": data,
        "evento_id": evento_id,
        "nombre": nombre,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "asociacion_id": asociacion_id,
        "capacidad": capacidad,
        "descripcion": descripcion
    }

    try:
        eventos = base.child("evento").get()
        for evento in eventos.each():
            print(evento.val()["evento_id"])
            if (evento.val()["evento_id"] == evento_id):
                if (nombre != ""):
                    base.child("evento").child(
                        evento.key()).update({"nombre": nombre})
                if (fecha_inicio != ""):
                    base.child("evento").child(evento.key()).update(
                        {"fecha_inicio": fecha_inicio})
                if (fecha_fin != ""):
                    base.child("evento").child(evento.key()).update(
                        {"fecha_fin": fecha_fin})
                if (asociacion_id != ""):
                    base.child("evento").child(evento.key()).update(
                        {"asociacion_id": asociacion_id})
                if (capacidad != ""):
                    base.child("evento").child(evento.key()).update(
                        {"capacidad": capacidad})
                if (descripcion != ""):
                    base.child("evento").child(evento.key()).update(
                        {"descripcion": descripcion})

                return jsonify({"message": "El evento se edito exitosamente"})

        return jsonify({"message": "Este evento no se ha encontrado"})

    except:
        return jsonify({"message": "Hubo un error al editar al evento"})

# Esta función elimina un evento
@api.route('/delete_evento', methods=["POST"])
def delete_evento():
    data = request.get_json()
    evento_id = data["evento_id"]

    try:
        eventos = base.child("evento").get()
        for evento in eventos.each():
            if (evento.val()["evento_id"] == evento_id):
                base.child("evento").child(evento.key()).remove()
                return jsonify({"message": "El evento se elimino exitosamente"})

        return jsonify({"message": "El evento no existe"})

    except:
        return jsonify({"message": "Hubo un error al eliminar al evento"})

# Esta función es un update de los eventos
@api.route('/update_capacidad', methods=["POST"])
def update_capacidad():
    data = request.get_json()
    evento_id = data["evento_id"]
    capacidad = data["capacidad"]

    nuevo_evento = {
        "data": data,
        "evento_id": evento_id,
        "capacidad": capacidad
    }

    try:
        eventos = base.child("evento").get()
        for evento in eventos.each():
            print(evento.val()["evento_id"])
            if (evento.val()["evento_id"] == evento_id):
                if (capacidad != ""):
                    base.child("evento").child(evento.key()).update(
                        {"capacidad": capacidad})
                return jsonify({"message": "El evento se edito exitosamente"})

        return jsonify({"message": "Este evento no se ha encontrado"})

    except:
        return jsonify({"message": "Hubo un error al editar al evento"})


############################################# Actividades ############################################

# Esta función crea una nueva actividad
@api.route('/crear_actividad', methods=["POST"])
def crear_actividad():
    data = request.get_json()
    evento_id = data["evento_id"]
    actividad_id = data["actividad_id"]
    nombre = data["nombre"]
    fecha = data["fecha"]
    hora_inicio = data["hora_inicio"]
    hora_fin = data["hora_fin"]
    descripcion = data["descripcion"]

    nueva_actividad = {
        "evento_id": evento_id,
        "actividad_id": actividad_id,
        "nombre": nombre,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "descripcion": descripcion
    }

    try:
        # Validates if the activity has already been registered
        eventos = base.child("evento").get()
        actividades = base.child("actividad").get()
        for evento in eventos.each():
            print(evento.val()["evento_id"])
            if (evento.val()["evento_id"] == evento_id):

                for actividad in actividades.each():
                    if (actividad.val()["actividad_id"] == actividad_id): 
                        return jsonify({"message": "La actividad ya existe"})
                    
                base.child("actividad").push(nueva_actividad)
                return jsonify({"message": "La actividad se registro exitosamente"})

        return jsonify({"message": "El evento no existe"})
        

    except:
        return jsonify({"message": "Hubo un error al agregar la actividad"})

# Get de las actividades
@api.route('/get_actividades', methods=["POST"])
def get_actividades():
    try:
        actividades = base.child("actividad").get().val()
        lista_actividades = list(actividades.values())
        return jsonify(lista_actividades)

    except:
        return jsonify({"message": "Hubo un error al consultar las actividades"})

# Esta función es un update de las actividades
@api.route('/update_actividad', methods=["POST"])
def update_actividad():
    data = request.get_json()
    evento_id = data["evento_id"]
    actividad_id = data["actividad_id"]
    nombre = data["nombre"]
    fecha = data["fecha"]
    hora_inicio = data["hora_inicio"]
    hora_fin = data["hora_fin"]
    descripcion = data["descripcion"]

    nueva_actividad = {
        "evento_id": evento_id,
        "actividad_id": actividad_id,
        "nombre": nombre,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "descripcion": descripcion
    }

    try:
        actividades = base.child("actividad").get()
        for actividad in actividades.each():
            if ((actividad.val()["evento_id"] == evento_id) and (actividad.val()["actividad_id"] == actividad_id)):
                if (nombre != ""):
                    base.child("actividad").child(
                        actividad.key()).update({"nombre": nombre})
                if (fecha != ""):
                    base.child("actividad").child(actividad.key()).update(
                        {"fecha": fecha})
                if (hora_inicio != ""):
                    base.child("actividad").child(actividad.key()).update(
                        {"hora_inicio": hora_inicio})
                if (hora_fin != ""):
                    base.child("actividad").child(actividad.key()).update(
                        {"hora_fin": hora_fin})
                if (descripcion != ""):
                    base.child("actividad").child(actividad.key()).update(
                        {"descripcion": descripcion})

                return jsonify({"message": "La actividad se edito exitosamente"})

        return jsonify({"message": "La actividad no se ha encontrado"})

    except:
        return jsonify({"message": "Hubo un error al editar la actividad"})


# Esta función elimina una actividad
@api.route('/delete_actividad', methods=["POST"])
def delete_actividad():
    data = request.get_json()
    evento_id = data["evento_id"]
    actividad_id = data["actividad_id"]

    try:
        actividades = base.child("actividad").get()
        for actividad in actividades.each():
            if ((actividad.val()["evento_id"] == evento_id) and (actividad.val()["actividad_id"] == actividad_id)):
                base.child("actividad").child(actividad.key()).remove()
                return jsonify({"message": "La actividad se elimino exitosamente"})

        return jsonify({"message": "La actividad no existe"})

    except:
        return jsonify({"message": "Hubo un error al eliminar la actividad"})


############################################# Estudiantes ############################################

# Crear un estudiante
@api.route('/crear_estudiante', methods=["POST"])
def crear_estudiante():
    data = request.get_json()
    carnet = data["carnet"]
    nombre = data["nombre"]
    correo = data["correo"]
    contrasena = data["contrasena"]

    nuevo_estudiante = {
        "carnet": carnet,
        "nombre": nombre,
        "correo": correo,
        "contrasena": contrasena
    }

    try:
        # Validates if the student has already been registered
        estudiantes = base.child("estudiante").get()
        for estudiante in estudiantes.each():
            print(estudiante.val()["carnet"])
            if (estudiante.val()["carnet"] == carnet):
                return jsonify({"message": "Este estudiante ya ha sido registrado"})

        base.child("estudiante").push(nuevo_estudiante)
        return jsonify({"message": "El estudiante se registro exitosamente"})

    except:
        return jsonify({"message": "Hubo un error al agregar al estudiante"})

# Esta función es un get de los estudiantes
@api.route('/get_estudiantes', methods=["POST"])
def get_estudiantes():
    try:
        estudiantes = base.child("estudiante").get().val()
        lista_estudiantes = list(estudiantes.values())
        return jsonify(lista_estudiantes)

    except:
        return jsonify({"message": "Hubo un error al consultar los estudiantes"})

# Esta función actualiza la información de un colaborador
@api.route('/uptade_estudiante', methods=["POST"])
def uptade_estudiante():
    data = request.get_json()
    carnet = data["carnet"]
    nombre = data["nombre"]
    correo = data["correo"]
    asociacion_id = data["asociacion_id"]
    es_organizador = data["es_organizador"]

    nuevo_colaborador = {
        "carnet": carnet,
        "nombre": nombre,
        "correo": correo,
        "asociacion_id": asociacion_id,
        "es_organizador": es_organizador

    }

    try:
        colaboradores = base.child("colaborador").get()
        for colaborador in colaboradores.each():
            print(colaborador.val()["carnet"])
            if (colaborador.val()["carnet"] == carnet):
                if (nombre != ""):
                    base.child("colaborador").child(
                        colaborador.key()).update({"nombre": nombre})
                if (correo != ""):
                    base.child("colaborador").child(
                        colaborador.key()).update({"correo": correo})
                if (asociacion_id != ""):
                    base.child("colaborador").child(colaborador.key()).update(
                        {"asociacion_id": asociacion_id})
                if (es_organizador != ""):
                    base.child("colaborador").child(colaborador.key()).update(
                        {"es_organizador": es_organizador})
                
                return jsonify({"message": "El colaborador se editó exitosamente"})

        return jsonify({"message": "Este colaborador no se ha encontrado"})

    except:
        return jsonify({"message": "Hubo un error al editar al colaborador"})

# Esta función elimina a un colaborador
@api.route('/delete_estudiante', methods=["POST"])
def delete_estudiante():
    data = request.get_json()
    carnet = data["carnet"]

    try:
        colaboradores = base.child("colaborador").get()
        for colaborador in colaboradores.each():
            if (colaborador.val()["carnet"] == carnet):
                base.child("colaborador").child(colaborador.key()).remove()
                return jsonify({"message": "El colaborador se elimino exitosamente"})

        return jsonify({"message": "El colaborador no existe"})

    except:
        return jsonify({"message": "Hubo un error al eliminar al colaborador"})






@api.route("/")
def hello():
    return "Welcome to Eventos-Tec"


if __name__ == "__main__":
    api.run(debug=True)
